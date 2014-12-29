# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4
import urllib
import re

def natgeo_pic_url():
    source_url = 'http://photography.nationalgeographic.com/photography/photo-of-the-day/'
    r = requests.get(source_url)
    soup = bs4.BeautifulSoup(r.text)
    for tag in soup.find_all('meta'):
        if tag.has_attr('property'):
            if tag['property'] == 'og:image':
                return tag['content']

def routers_imgs():
    reuters = "http://www.reuters.com/news/pictures"
    r = requests.get(reuters)
    soup = bs4.BeautifulSoup(r.text)
    images = [i for i in soup.find_all('img') 
    if i.has_attr('alt') and i['alt'] == "Photo"]
   
    img_urls = [urllib.unquote(img['src']).decode('utf8') for img in images]
    return [re.sub(r'w=300', r'w=620', i) for i in img_urls]

def main():
    for i in routers_imgs():
        print(i)


if __name__ == "__main__":
    main()