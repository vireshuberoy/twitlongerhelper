import os
import json
import time
from dotenv import load_dotenv
import tweepy
import logging
import re
from scraping import return_scrape

load_dotenv()

api_key = os.getenv("APIKEY")
api_secret_key = os.getenv("APISECRETKEY")
bearer_token = os.getenv("BEARERTOKEN")
access_token = os.getenv("ACCESSTOKEN")
access_token_secret = os.getenv("ACCESSTOKENSECRET")

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def check_mentions(api, since_id):
    logger.info("getting mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, int(new_since_id))

        if tweet._json['user']['screen_name'] == 'TwitlongerH':
            continue

        status_id_of_post = tweet._json['in_reply_to_status_id']
        twitlonger_link = api.get_status(status_id_of_post)._json['entities']['urls'][0]['expanded_url']

        res = re.match("(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", twitlonger_link)
        screen_name = tweet._json['user']['screen_name']
        if res:
            content_of_twitlonger = return_scrape(twitlonger_link)
            logger.info(content_of_twitlonger)
            n = 190
            parts = [content_of_twitlonger[i:i+n] for i in range(0, len(content_of_twitlonger), n)]
            first = True
            response = None
            reply_statement = ""
            for i, part_of_tweet in enumerate(parts):
                if first:
                    reply_statement = f"@{screen_name} This is the content: \n{part_of_tweet} {i + 1}/{len(parts)}"
                    first = False
                    response = api.update_status(status=reply_statement, in_reply_to_status_id=tweet.id)
                    time.sleep(2)
                    continue
                id_for_tweet = response._json['id']
                name = response._json['user']['screen_name']
                reply_statement = f"@{name} {part_of_tweet} {i + 1}/{len(parts)}"

                api.update_status(status=reply_statement, in_reply_to_status_id=id_for_tweet)
                time.sleep(2)
        else:
            api.update_status(status=f"@{screen_name} Parent post does not contain a link. Please make sure that you reply directly to the post containing the link", in_reply_to_status_id=tweet.id)
            print("Parent post does not contain a link")

    return new_since_id

since_id = 1
try:
    with open("since_id.txt", "r") as file:
        since_id = file.read()
except FileNotFoundError:
    pass

while True:
    since_id = check_mentions(api, since_id)
    with open("since_id.txt", 'w+') as file:
        file.write(str(since_id))
    time.sleep(60)
    logger.info("sleeping")
