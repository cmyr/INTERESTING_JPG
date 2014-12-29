# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4

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

def natgeo_pic_url():
    source_url = 'http://photography.nationalgeographic.com/photography/photo-of-the-day/'
    r = requests.get(source_url)
    soup = bs4.BeautifulSoup(r.text)
    for tag in soup.find_all('meta'):
        if tag.has_attr('property'):
            if tag['property'] == 'og:image':
                return tag['content']

def main():
    # descs = description(sample_response)
    # print(descs)
    # test_url = 'http://graphics8.nytimes.com/images/2014/12/28/opinion/sunday/2014-yip-august-slide-VNYR/2014-yip-august-slide-VNYR-jumbo.jpg'
    # r = response_for_image(test_url)
    # print(r.text)

    pic_url = natgeo_pic_url()
    r = response_for_image(pic_url)
    print(r.text)

    # print(r.text)
if __name__ == "__main__":
    main()