#!/usr/bin/env python3

import requests
# See: https://stackoverflow.com/questions/40768570/
from multiprocessing import Queue

import argparse
import json

from bs4 import BeautifulSoup

class ElibLoader:

    def __init__(self, url):
        self.bookUrl = url
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

    def loadBookInfo(self):
        resp = self.session.get(self.bookUrl)
        soup = BeautifulSoup(resp.text, 'html.parser')
        info = json.loads(soup.find_all('script')[1].text[15:-2])
        pageids = [x['id'] for x in info["pages"]]
        return pageids


    def loadpage(self, id, filename):
        """
        Load page on maximum zoom = 8
        """
        resp = self.session.get('http://elib.shpl.ru/pages/%d/zooms/8' % id)

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
    
def main():
    argparser = argparse.ArgumentParser(description='This program need to download books from elib.shpl.ru')
    argparser.add_argument('BOOK_URL', type=str)
    args = argparser.parse_args()

    ElibLoader(args.BOOK_URL).loadbook()

if __name__ == "__main__":
    main()
