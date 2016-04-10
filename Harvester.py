import tweepy
import time
#import couchdb
import os
import urllib
import json
from tweepy import Stream
from tweepy.streaming import StreamListener
#import simplejson
import datetime
from datetime import timedelta
import math
from textblob import TextBlob
# from geopy.geocoders import Nominatim
# import couch

from couchbase.bucket import Bucket
import couchbase.exceptions as E
cb = Bucket('couchbase://115.146.85.104/melbourne_tweets')

# access_token = "3254357972-gQDabKOQfbZJsSGyUVynYqckImVjizBDydjuxhX"
# access_secret = "rrGORFp6LW3MznoFKfCvkjNo3pAfpVPGb75Vv3rzv4xFF"
# consumer_key = "WdTNeWnGBzRHfuJGBN0xoCJxp"
# consumer_secret = "1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe"

consumer_key = "CwP9jWveyzDUC61XFb9iQTlfx";
consumer_secret = "yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI";
access_token = "1615559564-AXla3P6ErZuZJCYiWma0S6EoazOAF9LpHS7Zgk6";
access_secret = "2QgYfYnTkkQdsHdwJ5fzGgmpxDNmfHq3Yh72CCSol2psY";

# consumer_key = "7CQ1IAImnhdjQ5Tj8eB83LdMj";
# consumer_secret = "CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU";
# access_token = "2787646230-a4sEVXjIlHU8rslO2jpsf2lX2ksyOVQEm40VZrE";
# access_secret = "Cnb2Z3t83Iow5r6qCOldFsTSHDBM8nzP37RWWsd1sy9fW";

access_token_list = ['3254357972-gQDabKOQfbZJsSGyUVynYqckImVjizBDydjuxhX', '2787646230-a4sEVXjIlHU8rslO2jpsf2lX2ksyOVQEm40VZrE', '1615559564-AXla3P6ErZuZJCYiWma0S6EoazOAF9LpHS7Zgk6']
access_secret_list = ['rrGORFp6LW3MznoFKfCvkjNo3pAfpVPGb75Vv3rzv4xFF', 'CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU', 'yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI']
consumer_key_list = ['WdTNeWnGBzRHfuJGBN0xoCJxp', '7CQ1IAImnhdjQ5Tj8eB83LdMj', 'CwP9jWveyzDUC61XFb9iQTlfx']
consumer_secret_list = ['1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe', 'CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU', 'yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

def getTimeline(screenName):
    alltweets = []
    tweets = ''
    try:
        tweets = api.user_timeline(screen_name=screenName, count=200)
    except tweepy.TweepError:
        print("Time out...")
        time.sleep(120)
        pass
    except Exception as e:
        print ("getTimeline", e)
        pass
    return tweets

def add_sentiment_score(tweet):
    # add sentiment value to the tweet
    blob = TextBlob(tweet['text'])
    sentiment_polarity = blob.sentiment.polarity
    sentiment_subjectivity = blob.sentiment.subjectivity

    # create a nested json for sentiment score for the tweet
    sentiment_score = {}
    sentiment_score['polarity'] = sentiment_polarity
    sentiment_score['subjectivity'] = sentiment_subjectivity
    tweet['sentiment_score'] = sentiment_score
    return tweet

def check_location(tweet):
    if (tweet['coordinates'] != None):
        coordinates0 = tweet['coordinates']['coordinates'][0]
        coordinates1 = tweet['coordinates']['coordinates'][1]
    else:
        coordinates0 = 0
        coordinates1 = 0

    if tweet['place'] != None:
        placeFullName = tweet['place']['full_name']
    else:
        placeFullName = None
    if (coordinates0 > 144.39) & (coordinates0 < 145.76) & (coordinates1 > -38.26) & (coordinates1 < -37.4) | (placeFullName == 'Melbourne, Victoria'):
        return True
    else:
        return False

def save_tweet(tweets):
    while True:
        tweet = tweets.next()
        if tweet._json["coordinates"] != None:
            screenName = tweet._json["user"]["screen_name"]
            # alltweets = getTimeline(screenName)
            if check_location(tweet._json) == True:
                tweet._json = add_sentiment_score(tweet._json)
                #store to couchbase
                id = tweet._json['id']
                try:
                    cb.insert(str(id), tweet._json)
                except Exception, e:
                    continue
                print(tweet._json)


if __name__ == '__main__':
    tweets = tweepy.Cursor(api.search, result_type='recent',include_entities=True, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,geocode="-37.74031,145.759292,70km").items()
    save_tweet(tweets)
