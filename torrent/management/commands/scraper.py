from django.core.management.base import BaseCommand
from torrent.models import Torrent, Tracker, TrackerStat
from tracker_scraper import scrape

from urllib.parse import urlparse


class Command(BaseCommand):
    help = "Scrape tracker and update stats"

    def handle(self, *args, **kwargs):

        # Scrape and build a dictionary with tracker_id as key

        hashes=[]
        scrape_dict={}
        for tracker in Tracker.objects.all():
            scrape_dict[tracker.id]={}
            for torrent in TrackerStat.objects.filter(tracker_id=tracker.id):
                hashes.append(torrent.torrent.info_hash)
            try:
                if not hashes:
                    print("No Torrent for tracker: " + str(tracker))
                else:
                    scrape_dict[tracker.id]=scrape(tracker=tracker.url,hashes=hashes)
            except(TimeoutError):
                print("timeout")
            hashes=[]

        # scrape_dict={5: {'0062ffdee976404615a8b9f4c2eaa6d6717c7c65': {'seeds': 33, 'peers': 0, 'complete': 47}, '6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 15, 'peers': 0, 'complete': 15}}, 6: {'0062ffdee976404615a8b9f4c2eaa6d6717c7c65': {'seeds': 33, 'peers': 0, 'complete': 47}, '6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 15, 'peers': 0, 'complete': 15}}, 7: {'0062ffdee976404615a8b9f4c2eaa6d6717c7c65': {'seeds': 0, 'peers': 0, 'complete': 0}, '6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 1, 'peers': 0, 'complete': 1}}, 8: {'6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 1, 'peers': 0, 'complete': 1}}}

        # Parse the scraping result and update the DB
        for tracker_id in scrape_dict:
            for info_hash in scrape_dict[tracker_id]:
                torrent_obj = Torrent.objects.get(info_hash=info_hash)
                torrent = TrackerStat.objects.get(tracker_id=tracker_id, torrent_id=torrent_obj.id)
                torrent.seed = scrape_dict[tracker_id][info_hash]['seeds']
                torrent.leech = scrape_dict[tracker_id][info_hash]['peers']
                torrent.complete = scrape_dict[tracker_id][info_hash]['complete']
                torrent.save()

        # Update the torrent seed and leech with tracker stat level 0

        torrents=Torrent.objects.all()

        for t in torrents:
            t_stats=TrackerStat.objects.filter(torrent_id=t.id, level=0)[0]
            t.seed = t_stats.seed
            t.leech = t_stats.leech
            t.save()

           #self.stdout.write(absolute_path)