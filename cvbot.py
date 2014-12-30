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
import re

from twitter.oauth import OAuth
from twitter.api import Twitter, TwitterError, TwitterHTTPError

from twittercreds import (CONSUMER_KEY, CONSUMER_SECRET,
                          ACCESS_KEY, ACCESS_SECRET)

import imagefetching

POST_INTERVAL = 120
HISTORY_FILE_NAME = '.bothistory'
TEMP_IMAGE_FILE_NAME = 'tempimg'
HISTORY_LENGTH = 100


class TwitterBot(object):

    """
    posts stuff to twitter, periodically.
    """

    def __init__(self, name, image_func, post_interval=POST_INTERVAL, auth=None):
        super(TwitterBot, self).__init__()
        self.post_interval = post_interval * 60
        self.name = name
        self.history_name = HISTORY_FILE_NAME + '_' + name
        self.oauth = auth or OAuth(ACCESS_KEY, ACCESS_SECRET,
                                   CONSUMER_KEY, CONSUMER_SECRET)
        self.twitter = Twitter(auth=self.oauth, api_version='1.1')
        self.upload = Twitter(domain="upload.twitter.com", auth=self.oauth,
                              api_version='1.1')
        self.image_func = image_func
        clean_history(self.history_name)
        self.url_length = self.twitter_url_length()
        print('twitter short url length is %d' % self.url_length)

    def twitter_url_length(self):
        """
        look at me, being all 'best practices-y'
        (see https://dev.twitter.com/rest/reference/get/help/configuration)
        """
        length = 23  # current value as a fallback
        try:
            config = self.twitter.help.configuration()
            l = config.get('short_url_length')
            return l or length
        except Exception as err:
            print(err)
        return length

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
        img_urls = self.image_func()
        for link, img in img_urls:
            if not history_contains(img, self.history_name):
                add_to_history(img, self.history_name)
                print('fetching img: %s \n caption %s' % (img, link))
                caption = description(response_for_image(img).text)
                if not caption:
                    time.sleep(5 * 60)  # server might be down, retry in 5min
                    continue
                char_count = 140 - self.url_length
                if char_count < len(caption):
                    caption = self.trim_caption(caption, char_count)
                    # only append link if it will fit in the tweet
                elif link and len(caption) + self.url_length + 1 < char_count:
                    caption += '\n' + str(link)

                media_id = self.upload_media(img)
                if media_id:
                    print('posting caption: %s' % caption)
                    try:
                        self.twitter.statuses.update(status=caption,
                                                     media_ids=str(media_id))
                        return
                    except TwitterError as err:
                        print(err)
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

    def trim_caption(self, caption, target_length):
        from trimmings import trimmings
        trimmed = caption
        for string, sub in trimmings:
            trimmed = re.sub(string, sub, trimmed)
            if len(trimmed) <= target_length:
                return trimmed

        return trimmed[:target_length - 3] + '..'

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
        lines = lines[:HISTORY_LENGTH]
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
    headers = {
        'connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'User-agent': "@interesting_jpg v. 1.0",
        'From': 'http://www.twitter.com/interesting_jpg'}
    return requests.post(base_url, files=files, headers=headers)


def description(raw_text):
    if raw_text:
        soup = bs4.BeautifulSoup(raw_text, 'html.parser')
        try:
            return soup.li.get_text()
        except AttributeError as err:
            print(err)
            print(soup.prettify())
            return None

def main():
    from twittercreds import normauth, nsfwauth
    
    funcs = {
        'reuters': imagefetching.reuters_slideshow_imgs,
        'nsfw': imagefetching.reddit_nsfw_imgs
    }

    auths = {
        'reuters': normauth,
        'nsfw': nsfwauth
    }

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help="required argument")
    parser.add_argument(
        '-i', '--interval', type=int, help='post time interval')
    args = parser.parse_args()

    image_func = funcs.get(args.source)
    if not image_func:
        print('unknown source argument')
        sys.exit(1)

    kwargs = {
        'name': args.source,
        'image_func': image_func,
        'auth': auths[args.source]
    }

    if args.interval:
        kwargs['post_interval'] = args.interval
    bot = TwitterBot(**kwargs)
    bot.run()

if __name__ == "__main__":
    main()
