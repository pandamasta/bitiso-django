from tracker_scraper import scrape

scrape(
    tracker='udp://tracker.opentrackr.org:1337',
    hashes=[
        "8df6e26142615621983763b729f640372cf1fc34",
    ]
)
