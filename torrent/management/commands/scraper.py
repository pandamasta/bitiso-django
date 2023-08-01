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

        hashes=[]
        #for tracker in Tracker.objects.all():
        for tracker in Tracker.objects.filter(id="29"):

            #print(get_url_without_path(tracker.url))
            print(tracker.url)

            for torrent in TrackerStat.objects.filter(tracker_id=tracker.id):
                print(torrent.torrent_id)
                hashes.append(torrent.torrent_id)
            print(scrape(tracker=tracker.url,hashes=hashes))

           #self.stdout.write(absolute_path)

# scrape(
#     tracker='udp://tracker.opentrackr.org:1337',
#     hashes=[
#         "8df6e26142615621983763b729f640372cf1fc34",
#     ]
# )
