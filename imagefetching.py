# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4
import urllib
import re
from collections import namedtuple
from reuterssample import reuters_sample


LinkedPhoto = namedtuple('LinkedPhoto', ['link_url', 'img_url'  ])

def natgeo_pic_url():
    source_url = 'http://photography.nationalgeographic.com/photography/photo-of-the-day/'
    r = requests.get(source_url)
    soup = bs4.BeautifulSoup(r.text)
    for tag in soup.find_all('meta'):
        if tag.has_attr('property'):
            if tag['property'] == 'og:image':
                return tag['content']

def reuters_imgs():
    reuters = "http://www.reuters.com/news/pictures"
    r = requests.get(reuters)
    soup = bs4.BeautifulSoup(r.text)
    images = [i for i in soup.find_all('img') 
    if i.has_attr('alt') and i['alt'] == "Photo"]
   
    img_urls = [urllib.unquote(img['src']).decode('utf8') for img in images]
    return [re.sub(r'w=300', r'w=620', i) for i in img_urls]

def reuters_linked_images():
    reuters_base_url = "http://www.reuters.com"
    reuters_photos_url = "http://www.reuters.com/news/pictures"
    r = requests.get(reuters_photos_url)
    soup = bs4.BeautifulSoup(r.text)

    found_photos = list()
    photo_divs = soup.find_all('div', class_='photo')
    for div in photo_divs:
        link = div.find('a')
        img = div.find('img', alt='Photo')
        # we get a bunch of small versions, but we can resize them sneakily
        if img:
            img = re.sub(r'w=300', r'w=620', img.get('src'))    
        
        if link and img:
            found_photos.append(
                LinkedPhoto(reuters_base_url + link['href'], 
                    urllib.unquote(img).decode('utf8')
                    )
                )
    return found_photos

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