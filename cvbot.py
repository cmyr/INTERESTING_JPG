# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import requests
import time
import sys
import shutil
import random
import re
import random
import os

import cPickle as pickle
from twitter.oauth import OAuth
from twitter.api import Twitter, TwitterError, TwitterHTTPError

from twittercreds import (CONSUMER_KEY, CONSUMER_SECRET,
                          ACCESS_KEY, ACCESS_SECRET)

import imagefetching
import cvserver
import imagehash

POST_INTERVAL = 120
HISTORY_FILE_NAME = '.bothistory'
TEMP_IMAGE_FILE_NAME = '.tempimg'
HISTORY_LENGTH = 100

NO_POSTING = False
DEBUG = False


class TwitterBot(object):

    """
    posts stuff to twitter, periodically.
    """

    def __init__(
        self, name, image_func, post_interval=POST_INTERVAL, auth=None):
        super(TwitterBot, self).__init__()
        self.post_interval = post_interval * 60
        self.name = name
        self.history_name = HISTORY_FILE_NAME + '_' + name
        self.oauth = auth or OAuth(ACCESS_KEY, ACCESS_SECRET,
                                   CONSUMER_KEY, CONSUMER_SECRET)
        self.twitter = None
        self.upload = Twitter(domain="upload.twitter.com", auth=self.oauth,
                              api_version='1.1')
        self.image_func = image_func
        self.history = self.load_history()
        if not NO_POSTING:
            self.url_length = self.twitter_url_length()

    def twitter_connection(self):
        if self.twitter == None:
            self.twitter = Twitter(auth=self.oauth, api_version='1.1')
        return self.twitter

    def set_proc_title(self):
        try:
            import setproctitle
            setproctitle.setproctitle('CVBot_%s' % self.name)
        except ImportError:
            print("missing module: setproctitle")

    def twitter_url_length(self):
        """
        look at me, being all 'best practices-y'
        (see https://dev.twitter.com/rest/reference/get/help/configuration)
        """
        length = 23  # current value as a fallback
        try:
            config = self.twitter_connection().help.configuration()
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
                self.save_history()
                self.sleep(self.post_interval)

        except KeyboardInterrupt:
            print('exiting')
            self.save_history()
            sys.exit(0)

    def entertain_the_huddled_masses(self):
        linked_photo = self.get_next_image()
        if linked_photo != None:
            caption = self.get_caption(linked_photo)
            if not caption:
                return
            self.tweet(linked_photo.img_url, caption)

    def get_next_image(self):
        img_urls = self.image_func()
        if not img_urls:
            print('failed to fetch img urls')
            return
        self.update_status("fetched %d images" % len(img_urls))
        random.shuffle(img_urls)
        for linked_photo in img_urls:
            image_hash = imagehash.image_hash(linked_photo.img_url)
            if not self.history_contains(linked_photo.img_url, image_hash):
                self.update_status("found new image %s" % linked_photo.img_url)
                self.add_to_history(linked_photo.img_url, image_hash)
                return linked_photo
            else:
                self.update_status("skipping image %s" % linked_photo.img_url)
        print('found no new images')

    def get_caption(self, linked_photo):
        if NO_POSTING:
            return "fake caption"
        response = cvserver.response_for_image(
            linked_photo.img_url, self.name)
        if not response:
            print("no response from server")
            return None
        caption = self.format_caption(
            cvserver.top_caption(response), linked_photo.link_url)
        self.update_status("found caption: %s" % caption)
        return caption

    def format_caption(self, caption, link):
        char_count = 140 - self.url_length
        if char_count < len(caption):
            caption = self.trim_caption(caption, char_count)
            # only append link if it will fit in the tweet
        elif link and len(caption) + self.url_length + 1 < char_count:
            caption += '\n' + str(link)
        return caption

    def tweet(self, img_url, text):
        if NO_POSTING:
            print("fake posted tweet for url: %s" % img_url)
            return
        media_id = self.upload_media(img_url)
        if media_id:
            if DEBUG:
                print('using image at %s' % img_url)
                print('posting with caption: %s' % text)
            try:
                self.twitter_connection().statuses.update(status=text,
                                                          media_ids=str(media_id))
                return
            except TwitterError as err:
                print(err)
                return
        else:
            print('failed to fetch media ID')
            return

    def upload_media(self, img_url):
        self.save_image(img_url)
        with open(TEMP_IMAGE_FILE_NAME, 'rb') as f:
            response = self.upload.media.upload(media=f.read())
            media_id = response.get('media_id')
            if media_id:
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

    def sleep(self, interval, randomize=True):
        interval = int(interval)
        if randomize:
            randfactor = random.randrange(0, interval)
            interval = interval * 0.5 + randfactor
        sleep_chunk = 1  # seconds

        print('sleeping for %d minutes' % (interval / 60))

        while interval > 0:
            sleep_status = ' %s remaining \r' % format_seconds(interval)
            sys.stdout.write(sleep_status.rjust(35))
            sys.stdout.flush()
            time.sleep(sleep_chunk)
            interval -= sleep_chunk

        print('\n')

    def delete_last(self):
        account_info = self.twitter_connection().account.verify_credentials()
        user_name = account_info.get('screen_name')
        tweets = self.twitter_connection().statuses.user_timeline(
            screen_name=user_name)
        last = tweets[0]
        self.twitter_connection().statuses.destroy(id=last.get('id_str'))
        print("deleted %s" % last.get('text'))

    def load_history(self):
        history = dict()
        pickle_file = "%s.p" % self.history_name
        if not os.path.exists(pickle_file):
            # migrate old hashes if present
            if os.path.exists(self.history_name):
                with open(self.history_name) as oldFile:
                    old_hashes = oldFile.read().splitlines()
                    for oh in old_hashes:
                        history[oh] = 'None'
        else:
            history = pickle.load(open(pickle_file))
        if DEBUG:
            print("loaded %d items to history." % len(history))
        return history

    def history_contains(self, img_url, img_hash):
        for hhash, hurl in self.history.items():
            h_diff = imagehash.hex_to_hash(hhash) - img_hash
            if h_diff <= 6:  # arbitrary magic measure of closeness
                if DEBUG:
                    print('hash collision (diff %d):\n%s\n%s' %
                          (h_diff, img_url, hurl))
                return True
            if h_diff <= 16:
                print("low diff: %d" % h_diff)
            if hurl == img_url:
                if DEBUG:
                    print('url collision: \n%s' % img_url)
                return True
        return False

    def add_to_history(self, img_url, img_hash):
        if DEBUG:
            print("%s added to history" % img_url)
        self.history[str(img_hash)] = img_url

    def save_history(self):
        pickle_file = "%s.p" % self.history_name
        pickle.dump(self.history, open(pickle_file, 'wb'))
        if DEBUG:
            print("saved %d items to history" % len(self.history))

    def test_hashing(self):
        for i in range(100):
            linked_photo = self.get_next_image()
            sys.stdout.write("\rprocessed: %d" % i)
            sys.stdout.flush()


    def update_status(self, new_status):
        sys.stdout.write("\r%s" % new_status)
        sys.stdout.flush()



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




def test():
    global NO_POSTING, DEBUG
    NO_POSTING = True
    DEBUG = True

    from twittercreds import normauth
    bot = TwitterBot(
        name='nsfw', image_func=imagefetching.reddit_nsfw_imgs, post_interval=0.1)
    bot.run()


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
    parser.add_argument(
        '--test', help="test image hashing", action="store_true")
    parser.add_argument(
        '--delete', help="delete last posted tweet", action="store_true")
    parser.add_argument(
        '-v', '--verbose', help="print debug information", action="store_true")
    parser.add_argument(
        '-d', '--delay', help="set initial sleep interval", type=int)

    args = parser.parse_args()

    if args.verbose:
        global DEBUG
        DEBUG = True

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

    if args.delete:
        return bot.delete_last()

    if args.delay:
        bot.sleep(args.delay * 60, randomize=False)

    bot.run()

if __name__ == "__main__":
    main()
    # test()
