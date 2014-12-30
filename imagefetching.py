# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4
import urllib
import re
from collections import namedtuple
from reuterssample import reuters_sample


LinkedPhoto = namedtuple('LinkedPhoto', ['link_url', 'img_url'])


def natgeo_pic_url():
    source_url = 'http://photography.nationalgeographic.com/photography/photo-of-the-day/'
    r = requests.get(source_url)
    soup = bs4.BeautifulSoup(r.text)
    for tag in soup.find_all('meta'):
        if tag.has_attr('property'):
            if tag['property'] == 'og:image':
                return tag['content']


def reuters_slideshow_link():
    reuters_base_url = "http://www.reuters.com"
    reuters_photos_url = "http://www.reuters.com/news/pictures"
    r = requests.get(reuters_photos_url)
    soup = bs4.BeautifulSoup(r.text)
    div = soup.find('div', class_='photo')
    return reuters_base_url + div.find('a')['href']


def reuters_slideshow_imgs():
    link = reuters_slideshow_link()
    r = requests.get(link)
    soup = bs4.BeautifulSoup(r.text)
    slides = soup.find_all('div', class_="slide")
    print(slides)
    imgs = list()
    for slide in slides:
        try:
            img_link = slide.find('img')['data-lazy']
            img_link = urllib.unquote(img_link).decode('utf8')
            img_link = re.sub(r'&w=[0-9]+', r'&w=620', img_link)
            imgs.append(LinkedPhoto(None, img_link))
        except (KeyError, AttributeError, TypeError):
            print('error extracting image from slide: %s' % slide.prettify())
    return imgs


def main():
    imgs = reuters_slideshow_imgs()
    print(imgs)

if __name__ == "__main__":
    main()
