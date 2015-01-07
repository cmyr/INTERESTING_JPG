# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import bs4
import re

def response_for_image(image_url):
    base_url = 'http://deeplearning.cs.toronto.edu/api/url.php'
    files = {
        'urllink': ('', image_url),
        'url-2txt': ('', '')
    }
    headers = {
        'connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'User-agent': "@interesting_jpg %s v. 1.0" % self.name
        # 'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5"
        }
    r = requests.post(base_url, files=files, headers=headers)
    text = r.text.strip()
    if not len(text):
        print('no text in response. status: %d %s' % (r.status_code, r.reason))
        return None
    return text


def description(raw_text):
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
    captions = header.find_next_sibling().find_all('li')
    return [c.text for c in captions]



def main():
    sample_response = """<img id="result-img" src="../tmpfiles/20150107-10:35:13.jpg" height="300"/><h4>TAGS:</h4><h4>&nbsp;&nbsp;cycler&nbsp;&nbsp;peddler&nbsp;&nbsp;salesman&nbsp;&nbsp;rucksack&nbsp;&nbsp;pedicab&nbsp;&nbsp;</h4><br/><h4>Nearest Neighbor Sentence:</h4><ul><li>a woman outside with an umbrella riding a motor cart .</li></ul><br/><h4>Top-5 Generated:</h4><ul><li>two men are wearing a hat , riding on a bicycle with a backpack .</li><li>a man in a cart filled with bikes .</li><li>a man wearing a hat while trying to ride a bicycle on a bike .</li><li>a man riding a bicycle with a cart attached .</li><li>a man wearing a hat on a bicycle and carrying a cart .
    </li></ul>"""

    captions(sample_response)
    # soup = bs4.BeautifulSoup(sample_response)
    # # print(soup.prettify())
    # headers = soup.find('h4', text=re.compile(r'Top'))
    # print(headers.find_next_sibling().li.string)
    # print(type(headers))
    # print([h.string for h in headers])


if __name__ == "__main__":
    main()