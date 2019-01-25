#!/usr/bin/env python3

import requests
# See: https://stackoverflow.com/questions/40768570/
from multiprocessing import Queue

import argparse
import json

from bs4 import BeautifulSoup

def loadBookInfo(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    info = json.loads(soup.find_all('script')[1].text[15:-2])
    pageids = [x['id'] for x in info["pages"]]
    return pageids

def loadpage(id, filename):
    """
    Load page on maximum zoom = 8
    """
    resp = requests.get('http://elib.shpl.ru/pages/%d/zooms/8' % id)
    
    with open(filename, 'wb') as f:
        for chunk in resp.iter_content(1024):
            f.write(chunk)
    

def loadbook(url):
    pageids = loadBookInfo(url)
    totalpages = len(pageids)
    print("Info loaded: %d pages was found" % len(pageids))
    
    # Filename mask
    fnmask = "{:0>%dd}.jpeg" % len(str(totalpages))
    
    for idx, id in enumerate(pageids):
        pagenum = idx + 1
        filename = fnmask.format(pagenum)
        loadpage(id, filename)
        print("Page %d successfully saved to %s" % (pagenum, filename))
    
def main():
    argparser = argparse.ArgumentParser(description='This program need to download books from elib.shpl.ru')
    argparser.add_argument('BOOK_URL', type=str)
    args = argparser.parse_args()

    loadbook(args.BOOK_URL)

if __name__ == "__main__":
    main()
