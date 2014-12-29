# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4

import imagefetching

def response_for_image(image_url):
    base_url = 'http://deeplearning.cs.toronto.edu/api/url.php'
    files = {
    'urllink': ('', image_url),
    'url-2txt': ('', '')
    }
    headers = {'connection': 'keep-alive', 'X-Requested-With': 'XMLHttpRequest'}
    return requests.post(base_url, files=files, headers=headers)


def description(raw_text):
    soup = bs4.BeautifulSoup(raw_text, 'html.parser') 
    return soup.li.get_text()


def main():
    pic_url = imagefetching.natgeo_pic_url()
    if pic_url:
        r = response_for_image(pic_url)
        print(description(r.text))

    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()


if __name__ == "__main__":
    main()