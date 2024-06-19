from django.core.management.base import BaseCommand
from torrent.models import Torrent, Tracker, TrackerStat
from tracker_scraper import scrape
from bencodepy.exceptions import BencodeDecodeError

from urllib.parse import urlparse
import urllib3


class Command(BaseCommand):
    help = "Scrape tracker and update stats"

    def handle(self, *args, **kwargs):

        # Scrape and build a dictionary with tracker_id as key

        hashes = []
        scrape_dict = {}
        for tracker in Tracker.objects.all():
            scrape_dict[tracker.id] = {}
            for torrent in TrackerStat.objects.filter(tracker_id=tracker.id):
                hashes.append(torrent.torrent.info_hash)
            try:
                if not hashes:
                    print("No Torrent for tracker: " + str(tracker))
                #elif tracker.url.startswith("http://tracker.bitiso.org"):
                #    print(f"No scrape support for tracker: {tracker.url}")
                else:
                    scrape_dict[tracker.id] = scrape(tracker=tracker.url, hashes=hashes)
            except TimeoutError:
                print("Timeout Error with tracker: " + str(tracker.url))
            except BencodeDecodeError:
                print(f"Error: Invalid bencoded data received from tracker: {tracker.url}")
            except ConnectionRefusedError:
                print(f"Connection Refused Error: Could not connect to tracker: {tracker.url}")
            except urllib3.exceptions.NewConnectionError as e:
                print(f"Network Error: Failed to establish a new connection to {tracker.url}: {str(e)}")
            except Exception as e:
                print(f"Unexpected Error: {str(e)}")
            finally:
                hashes = []  # Clearing the hashes list for the next iteration scraping result and update the DB
        for tracker_id in scrape_dict:
            for info_hash in scrape_dict[tracker_id]:
                torrent_obj = Torrent.objects.get(info_hash=info_hash)
                torrent = TrackerStat.objects.get(tracker_id=tracker_id, torrent_id=torrent_obj.id)
                torrent.seed = scrape_dict[tracker_id][info_hash]['seeds']
                torrent.leech = scrape_dict[tracker_id][info_hash]['peers']
                torrent.complete = scrape_dict[tracker_id][info_hash]['complete']
                torrent.save()

        # Update the torrent seed and leech with tracker stat level 0

        torrents = Torrent.objects.all()

        for t in torrents:
            t_stats = TrackerStat.objects.filter(torrent_id=t.id, level=0)[0]
            t.seed = t_stats.seed
            t.leech = t_stats.leech
            t.save()
