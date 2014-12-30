# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import bs4
import requests
import time
import sys
import shutil
import random
import json

from twitter.oauth import OAuth
from twitter.api import Twitter, TwitterError, TwitterHTTPError

from twittercreds import (CONSUMER_KEY, CONSUMER_SECRET,
                        ACCESS_KEY, ACCESS_SECRET)

import imagefetching

POST_INTERVAL = 10
HISTORY_FILE_NAME = '.bothistory'
TEMP_IMAGE_FILE_NAME = 'tempimg'

class TwitterBot(object):

    """
    posts stuff to twitter, periodically.
    """

    def __init__(self, post_interval=POST_INTERVAL, debug=False):
        super(TwitterBot, self).__init__()
        self._debug = debug
        self.post_interval = post_interval * 60
        self.oauth = OAuth(ACCESS_KEY, ACCESS_SECRET,
            CONSUMER_KEY, CONSUMER_SECRET)
        self.twitter = Twitter(auth=self.oauth, api_version='1.1')
        self.upload = Twitter(domain="upload.twitter.com", auth=self.oauth,
            api_version='1.1')
        clean_history()

    def run(self):
        print('CVBot running')
        try:
            while True:
                self.entertain_the_huddled_masses()
                self.sleep(self.post_interval)

        except KeyboardInterrupt:
            print('exiting')
            sys.exit(0)

    def entertain_the_huddled_masses(self):
        img_urls = imagefetching.reuters_imgs()
        for img in img_urls:
            if not history_contains(img):
                add_to_history(img)
                print('fetching img: %s' % img)
                caption = description(response_for_image(img).text)
                media_id = self.upload_media(img)
                if media_id:
                    print('posting caption: %s' % caption)
                    self.twitter.statuses.update(status=caption,
                        media_ids=str(media_id))
                    return
                else:
                    print('failed to fetch media ID')
                    return
        print('found no new images')

    def upload_media(self, img_url):
        self.save_image(img_url)
        with open(TEMP_IMAGE_FILE_NAME, 'rb') as f:
            response = self.upload.media.upload(media=f.read())
            media_id = response.get('media_id')
            if media_id:
                print('uploaded image with id %s' % media_id)
                return media_id

    def save_image(self, image_url):
        response = requests.get(image_url, stream=True)
        with open(TEMP_IMAGE_FILE_NAME, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)

    def sleep(self, interval):
        interval = int(interval)
        randfactor = random.randrange(0, interval)
        interval = interval * 0.5 + randfactor
        sleep_chunk = 10  # seconds

        print('sleeping for %d minutes' % (interval / 60))

        while interval > 0:
            sleep_status = ' %s remaining \r' % format_seconds(interval)
            sys.stdout.write(sleep_status.rjust(35))
            sys.stdout.flush()
            time.sleep(sleep_chunk)
            interval -= sleep_chunk

        print('\n')

def clean_history(filename=HISTORY_FILE_NAME):
    try:
        lines = open(filename, 'r').readlines()
        lines = lines[:20]
        with open(filename, 'w') as f:
            f.writelines(lines)
    except IOError as err:
        print('ioerror! %s' % err)
        f = open(filename, 'w')
        f.close()

def add_to_history(text, filename=HISTORY_FILE_NAME):
    with open(filename, 'a') as f:
        f.write(text + '\n')
        f.flush()

def history_contains(text, filename=HISTORY_FILE_NAME):
    with open(filename) as f:
        for line in f:
            print(line)
            if line.strip() == text.strip():
                return True
    return False

    # def send_dm(self, message):
    #     """sends me a DM if I'm running out of haiku"""
    #     try:
    #         self.twitter.direct_messages.new(user=BOSS_USERNAME, text=message)
    #     except TwitterError as err:
    #         print(err)

def format_seconds(seconds):
    """
    convert a number of seconds into a custom string representation
    """
    d, seconds = divmod(seconds, (60 * 60 * 24))
    h, seconds = divmod(seconds, (60 * 60))
    m, seconds = divmod(seconds, 60)
    time_string = ("%im %0.2fs" % (m, seconds))
    if h or d:
        time_string = "%ih %s" % (h, time_string)
    if d:
        time_string = "%id %s" % (d, time_string)
    return time_string

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

def test_history_stuff():
    clean_history()

    some_lines = imagefetching.reuters_imgs()
    for line in some_lines:
        add_to_history(line)

    for line in some_lines[:2]:
        if not history_contains(line):
            print('history is missing line %s' % line)


def main():
    # testurl = "http://s2.reutersmedia.net/resources/r/?m=02&d=20141229&t=2&i=1008323401&w=620&fh=&fw=&ll=&pl=&r=2014-12-29T125516Z_2_GM1EACT0WFC01_RTRMADP_0_INDONESIA-AIRPLANE"
    # testurl = "http://www.nationalgeographic.com/dc/exposure/homepage/photoconfiguration/image/45931_photo_bbeogq2ezjz6gatzmuj7agam73vu2hmpyjyavf6lo6pvvsfavj3q_850x478.jpg"
    # save_image(testurl)
    bot = TwitterBot()
    # bot.upload_media(testurl)
    bot.run()
    # test_history_stuff()

    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()


if __name__ == "__main__":
    main()