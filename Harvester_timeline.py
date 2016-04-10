# Supervisor : Prof. Richard Sinnott
# Subject: COMP90055 COMPUTING PROJECT

import tweepy
import time
import couchdb
import os
import pickle
import jsonpickle
import urllib
import json
from tweepy import Stream
from tweepy.streaming import StreamListener
import simplejson
import datetime
from datetime import timedelta
import math
from nltk.corpus import wordnet as wn
from textblob import TextBlob
# import googlemaps

from couchbase.bucket import Bucket
import couchbase.exceptions as E
cb = Bucket('couchbase://115.146.85.104/default')

consumer_key = "7CQ1IAImnhdjQ5Tj8eB83LdMj";
consumer_secret = "CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU";
access_token = "2787646230-a4sEVXjIlHU8rslO2jpsf2lX2ksyOVQEm40VZrE";
access_secret = "Cnb2Z3t83Iow5r6qCOldFsTSHDBM8nzP37RWWsd1sy9fW";

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
#when reach limit, recovery automatically
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]))
# gmaps = googlemaps.Client(key='AIzaSyDeIQ2brFZT6RAL2MULaQJaAelTaWDTxdc')

usernames_file_path = "/home/ubuntu/Harvester/streamUsername.txt"
all_usernames = []

def getTimeline(screenName):
    # timeline_tweets = []
    timeline_tweets = ''
    try:
        timeline_tweets = api.user_timeline(screen_name=screenName, count=200)
    except Exception as e:
        print ("getTimeline", e)
        pass
    except tweepy.TweepError:
        print("Time out, please wait...")
        time.sleep(60)
        pass
    return timeline_tweets

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


def save_username(username):
	match = username not in all_usernames
	if match:
		all_usernames.append(username)
		with open(usernames_file_path,'a') as f:
			f.write(username+", ")
			return True
	else:
		return False

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


def save_tweet(tweet):
    timeline_tweets = []
    pickled = jsonpickle.encode(tweet)
    results = json.loads(pickled)
    doc = results['py/state']['_json']
    doc = add_sentiment_score(tweet._json)
    #store to couchbase
    id = tweet._json['id']
    cb.insert(str(id), tweet._json)
    print("doc: ",doc)

    # check if the user name if list, if not search the timeline
    if check_location(tweet._json) == True:
        screenName = doc["user"]["screen_name"]
        if save_username(screenName) == True:
            timeline_tweets = getTimeline(screenName)
            for t in timeline_tweets:
                if check_location(t._json) == True:
                    t = add_sentiment_score(t._json)
                    print(t)			
	                # store tweets to couchbase
                    id = t['id']
                    try:
                        cb.insert(str(id), t)
                    except Exception, e:
                        continue

with open(usernames_file_path, 'r') as outfile:
    for line in outfile.readlines():
        all_usernames = line.split(',')

class MyListener(StreamListener):
 
    def on_status(self, status):

        save_tweet(status)
    def on_error(self, status):
        print(status)
        return True
    def on_timeout(self):
        return True

if __name__ == '__main__':
    l = MyListener()
    print ("Steaming starts!")
    stream = tweepy.Stream(auth, l)
    stream.filter(locations=[144.4701516,-37.8394484,144.9411904,-37.6398952])
