#!/usr/bin/env python
"""Simple script to scrape a tracker"""
import bencode
import urllib.request

SCRAPE_URL = 'http://tracker.bitiso.org:6969/scrape'

def scrape(url=SCRAPE_URL):
    """Return dict of scrape results"""
    try:
        with urllib.request.urlopen(url) as response:
            binary_file = response.read()
            print(binary_file)
            return bencode.bdecode(response.read())
    except(urllib.error.URLError):
        print("Connection Refused")

def print_scrape():
    """Print files with pprint"""
    from pprint import pprint
    data = scrape()
    files = data['files']
    for file_hash in files:
        pprint(file_hash)
        pprint(files[file_hash])

if __name__ == '__main__':
    print_scrape()