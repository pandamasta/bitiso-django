from django.core.management.base import BaseCommand
from torrent.models import Tracker, TrackerStat
from tracker_scraper import scrape

from urllib.parse import urlparse


class Command(BaseCommand):
    help = "Scrape tracker and update stats"

    def handle(self, *args, **kwargs):

        # def get_url_without_path(url):
        #     parsed_url = urlparse(url)
        #     url_without_path = f"{parsed_url.scheme}://{parsed_url.netloc}"
        #     return url_without_path

        # Scrape and build a dictionary with tracker_id as key

        # hashes=[]
        # scrape_dict={}
        # for tracker in Tracker.objects.all():
        #     scrape_dict[tracker.id]={}
        #     print(tracker.url)
        #     for torrent in TrackerStat.objects.filter(tracker_id=tracker.id):
        #         print(torrent.torrent_id)
        #         hashes.append(torrent.torrent_id)
        #     scrape_dict[tracker.id]=scrape(tracker=tracker.url,hashes=hashes)
        #     hashes=[]

        scrape_dict={5: {'0062ffdee976404615a8b9f4c2eaa6d6717c7c65': {'seeds': 33, 'peers': 0, 'complete': 47}, '6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 15, 'peers': 0, 'complete': 15}}, 6: {'0062ffdee976404615a8b9f4c2eaa6d6717c7c65': {'seeds': 33, 'peers': 0, 'complete': 47}, '6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 15, 'peers': 0, 'complete': 15}}, 7: {'0062ffdee976404615a8b9f4c2eaa6d6717c7c65': {'seeds': 0, 'peers': 0, 'complete': 0}, '6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 1, 'peers': 0, 'complete': 1}}, 8: {'6fa58258c686ef73df6b4fb34b6d2c07cf0afadd': {'seeds': 1, 'peers': 0, 'complete': 1}}}

        # Parse the scraping result and update the DB

        for tracker_id in scrape_dict:
            for info_hash in scrape_dict[tracker_id]:
                print(scrape_dict[tracker_id][info_hash])
                torrent = TrackerStat.objects.get(tracker_id=tracker_id, torrent_id=info_hash)
                torrent.seed = scrape_dict[tracker_id][info_hash]['seeds']
                torrent.peers = scrape_dict[tracker_id][info_hash]['peers']
                torrent.save()
           #self.stdout.write(absolute_path)