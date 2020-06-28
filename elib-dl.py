#!/usr/bin/env python3

import re
import sys
import signal
import requests
import traceback
# See: https://stackoverflow.com/questions/40768570/
from multiprocessing import Queue

import argparse
import json

from sys import stderr
from urllib.parse import urlparse, urlunparse

class ElibLoader:

    def __init__(self, url):
        self.bookUrl = urlparse(url)
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

    def loadBookInfo(self):
        resp = self.session.get(
            urlunparse(self.bookUrl),
            headers={
                "Accept": "text/html; charset=utf-8"
            })

        print("Response content-type: %s" % resp.headers["content-type"])
        print("Requests encoding: %s" % resp.encoding)

        # For some reason some of Windows users recieves
        # the page encoded in cp1251 encoding.
        resp.encoding = 'utf-8'

        html = resp.text

        m = re.search(r"<script>.*$\s+(.*)", html, re.M)

        if m:
            pagesJson = m.group(1).strip()[12:-1]

            info = json.loads(pagesJson)
            pageids = [x['id'] for x in info["pages"]]
            return pageids
        else:
            print("Failed to find script block", file=stderr)
            with open('dump.html', 'wb') as f:
                f.write(resp.content)
            with open('dump-text.html', 'w') as f:
                print(html, file=f)

    def loadpage(self, id, filename):
        """
        Load page on maximum zoom = 8
        """
        resp = self.session.get(urlunparse((
            self.bookUrl.scheme, self.bookUrl.netloc, '/pages/%d/zooms/8' % id,
            None, None, None)))

        resp.raise_for_status()

        with open(filename, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)


    def loadbook(self):
        pageids = self.loadBookInfo()
        totalpages = len(pageids)

        print("Info loaded: %d pages was found" % len(pageids))

        # Filename mask
        fnmask = "{:0>%dd}.jpeg" % len(str(totalpages))

        for idx, id in enumerate(pageids):
            pagenum = idx + 1
            filename = fnmask.format(pagenum)
            self.loadpage(id, filename)
            print("Page %d successfully saved to %s" % (pagenum, filename))

def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    argparser = argparse.ArgumentParser(description='This program need to download books from elib.shpl.ru')
    argparser.add_argument('BOOK_URL', type=str)
    args = argparser.parse_args()

    ElibLoader(args.BOOK_URL).loadbook()

if __name__ == "__main__":
    main()
