# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import bs4

import imagefetching
import time
import sys
import random
import json

from twitter.oauth import OAuth
from twitter.api import Twitter, TwitterError, TwitterHTTPError

from twittercreds import (CONSUMER_KEY, CONSUMER_SECRET,
                        ACCESS_KEY, ACCESS_SECRET)


POST_INTERVAL = 120
HISTORY_FILE_NAME = '.bothistory'

class TwitterBot(object):

    """
    posts stuff to twitter, periodically.
    """

    def __init__(self, post_interval=POST_INTERVAL, debug=False):
        super(HaikuDemon, self).__init__()
        self._debug = debug
        self.post_interval = post_interval * 60
        self.twitter = twitter = Twitter(
            auth=OAuth(ACCESS_KEY,
                       ACCESS_SECRET,
                       CONSUMER_KEY,
                       CONSUMER_SECRET),
            api_version='1.1')

    def run(self):
        try:
            while True:
                # self.entertain_the_huddled_masses()
                self.sleep(self.post_interval)

        except KeyboardInterrupt:
            print('exiting')
            sys.exit(0)

    # def entertain_the_huddled_masses(self):
    #     haiku = haikuwriter.a_solitary_poem()
    #     self.post(haiku)


    def post(self, post_text):
        if self._debug:
            print(post_text)
            return True

        try:
            success = self.twitter.statuses.update(status=post_text)
            print('posted haiku:\n\n%s' % post_text)
            return success
        except TwitterError as err:
            http_code = err.e.code

            if http_code == 403:
                # get the response from the error:
                response = json.JSONDecoder().decode(err.response_data)
                response = response.get('errors')
                if response:
                    response = response[0]

                    error_code = int(response.get('code'))
                    if error_code == 187:
                        print('attempted to post duplicate')
                        # status is a duplicate
                        return True
                    else:
                        print('unknown error code: %d' % error_code)

            else:
                # if http_code is *not* 403:
                print('received http response %d' % http_code)
                # assume either a 404 or a 420, and sleep for 10 mins
                time.sleep(600)
                return False

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
            print('**  ', line)
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

    some_lines = imagefetching.routers_imgs()
    for line in some_lines:
        add_to_history(line)

    for line in some_lines[:2]:
        if not history_contains(line):
            print('history is missing line %s' % line)



def main():
    test_history_stuff()

    # pic_url = imagefetching.natgeo_pic_url()
    # if pic_url:
    #     r = response_for_image(pic_url)
    #     print(description(r.text))

    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()


if __name__ == "__main__":
    main()