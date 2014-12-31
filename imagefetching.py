# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4
import urllib
import re
from collections import namedtuple


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
    imgs = list()
    for slide in slides:
        try:
            img_link = slide.find('img')['data-lazy']
            img_link = urllib.unquote(img_link).decode('utf8')
            img_link = re.sub(r'&w=[0-9]+', r'&w=620', img_link)
            imgs.append(LinkedPhoto(None, img_link))
        except (KeyError, AttributeError, TypeError):
            pass
    return imgs

def reddit_nsfw_imgs():
    url = "http://www.reddit.com/over18?dest=http%3A%2F%2Fwww.reddit.com%2Fr%2Fblowjobs%2Bcreampies%2Bcumsluts%2Bdirtysmall%2Bfacesitting%2BGirlsFinishingTheJob%2Bnsfwhardcore%2Bbroslikeus%2BCuteGuyButts%2Bforeskin%2BGaybrosGoneWild%2Bgaycumsluts%2Bgaynsfw%2Bgayporn%2BGaySex%2BMassiveCock%2Bpenis
    headers = {'User-agent': '@interesting_jpg v0.9'}
    params = {'uh': '', 'over18': 'yes'}
    r = requests.post(url, params=params, headers=headers)
    soup = bs4.BeautifulSoup(r.text)
    things = soup.find_all('div', class_="thing")
    pixxx = [t.find('a', class_='thumbnail') for t in things]
    pixxx = [t['href'] for t in pixxx if t]
    pixxx = [t for t in pixxx if t and re.search('\.(jpg|jpeg|png)', t, flags=re.IGNORECASE)]
    return [LinkedPhoto(None, t) for t in pixxx]

def main():
    for img in reddit_nsfw_imgs():
        print(img)

if __name__ == "__main__":
    main()
