# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4
import re

from cvbot import DEBUG

def response_for_image(image_url, client_name):
    base_url = 'http://deeplearning.cs.toronto.edu/api/url.php'
    files = {
        'urllink': ('', image_url),
        'url-2txt': ('', '')
    }
    headers = {
        'connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'User-agent': "@interesting_jpg %s v. 1.0" % client_name
    }

    r = requests.post(base_url, files=files, headers=headers, timeout=5*60)
    text = r.text.strip()
    if DEBUG:
        print(r)
    if not len(text):
        print('no text in response. status: %d %s' % (r.status_code, r.reason))
        return None
    return text


def nearest_neighbour(raw_text):
    if raw_text:
        soup = bs4.BeautifulSoup(raw_text, 'html.parser')
        try:
            return soup.li.get_text()
        except AttributeError as err:
            print(err)
            print(soup.prettify())
            return None


def captions(raw_text):
    soup = bs4.BeautifulSoup(raw_text)
    header = soup.find('h4', text=re.compile(r'Top'))
    if not header:
        print('error parsing text')
        print(soup.prettify())
        return
    if DEBUG:
        print(header.find_next_sibling().prettify())
    next_sib = header.find_next_sibling()
    if next_sib:
        captions = next_sib.find_all('li')
        if captions:
            return [c.text for c in captions]
    print("no captions found?")
    print(soup.prettify())


def top_caption(raw_text):
    all_captions = captions(raw_text)
    if DEBUG:
        print(all_captions)
    if all_captions:
        return all_captions[0]


def main():
    sample_response = """<img id="result-img" src="../tmpfiles/20150107-10:35:13.jpg" height="300"/><h4>TAGS:</h4><h4>&nbsp;&nbsp;cycler&nbsp;&nbsp;peddler&nbsp;&nbsp;salesman&nbsp;&nbsp;rucksack&nbsp;&nbsp;pedicab&nbsp;&nbsp;</h4><br/><h4>Nearest Neighbor Sentence:</h4><ul><li>a woman outside with an umbrella riding a motor cart .</li></ul><br/><h4>Top-5 Generated:</h4><ul><li>two men are wearing a hat , riding on a bicycle with a backpack .</li><li>a man in a cart filled with bikes .</li><li>a man wearing a hat while trying to ride a bicycle on a bike .</li><li>a man riding a bicycle with a cart attached .</li><li>a man wearing a hat on a bicycle and carrying a cart .
    </li></ul>"""

    print("\n".join(captions(sample_response)))
    print(top_caption(sample_response))


if __name__ == "__main__":
    main()
