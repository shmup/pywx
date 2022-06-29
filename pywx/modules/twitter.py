import logging
from urllib.parse import urlparse

import requests

from .base import ParserCommand
from .registry import register_parser


@register_parser
class TwitterParser(ParserCommand):
    def parse(self, msg):
        lines = []
        for word in msg['msg'].split(' '):
            url = urlparse(word)
            if 'twitter' in url.netloc:
                path = url.path
                try:
                    username = path.split('/')[1]
                    twid = path.split('/')[3]

                    data = requests.get("https://api.twitter.com/2/tweets", params={'ids': twid}, headers={'Authorization': f'Bearer {self.config["twitter_token"]}'}).json()
                    if 'errors' in data:
                        continue

                    tweet = data['data'][0]['text']
                    tweetlines = []
                    for tweetline in tweet.split('\n'):
                        if not tweetline:
                            continue
                        if len(tweetlines) == 0:
                            tweetlines.append(f'@{username}: {tweetline}')
                        else:
                            tweetlines.append(f'{tweetline}')
                    lines.extend(tweetlines)
                except Exception: # pylint: disable=broad-except
                    logging.exception("twitter problem")
        return lines
