#!/usr/bin/env python3

import requests
import sys
import signal
import re
import argparse

class KanebLoader:

    def __init__(self, url):
        self.url = url
        self.index = []

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

    def loadIndex(self):
        '''
        Загрузка списка страниц
        '''
        resp = self.session.get(self.url)
        resp.raise_for_status()

        html = resp.text

        for m in re.finditer(r"/FileStore/dataFiles/fe/\d+/\d+/content/[^\"]+", html):
            self.index.append("https://kazneb.kz" + m.group(0).replace("amp;", ''))

        print("Index of pages was loaded: %d" % len(self.index))

    def loadBook(self):

        for idx, pageUrl in enumerate(self.index):
            print("Loading page: %d.png" % idx)
            resp = self.session.get(pageUrl)
            resp.raise_for_status()

            with open("%d.png" % idx, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)


def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    argparser = argparse.ArgumentParser(description='This program need to download books from elib.shpl.ru')
    argparser.add_argument('BOOK_URL', type=str)
    args = argparser.parse_args()

    loader = KanebLoader(args.BOOK_URL)
    loader.loadIndex()
    loader.loadBook()

if __name__ == "__main__":
    main()
