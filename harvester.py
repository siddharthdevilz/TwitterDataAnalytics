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
from geopy.geocoders import Nominatim

import couch

access_token = "3254357972-gQDabKOQfbZJsSGyUVynYqckImVjizBDydjuxhX"
access_secret = "rrGORFp6LW3MznoFKfCvkjNo3pAfpVPGb75Vv3rzv4xFF"
consumer_key = "WdTNeWnGBzRHfuJGBN0xoCJxp"
consumer_secret = "1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe"

access_token_list = ['3254357972-gQDabKOQfbZJsSGyUVynYqckImVjizBDydjuxhX', '2787646230-a4sEVXjIlHU8rslO2jpsf2lX2ksyOVQEm40VZrE', '1615559564-AXla3P6ErZuZJCYiWma0S6EoazOAF9LpHS7Zgk6']
access_secret_list = ['rrGORFp6LW3MznoFKfCvkjNo3pAfpVPGb75Vv3rzv4xFF', 'CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU', 'yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI']
consumer_key_list = ['WdTNeWnGBzRHfuJGBN0xoCJxp', '7CQ1IAImnhdjQ5Tj8eB83LdMj', 'CwP9jWveyzDUC61XFb9iQTlfx']
consumer_secret_list = ['1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe', 'CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU', 'yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI']

overall_count = 0
count_error = 0


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#couch = couchdb.Server()
#couch = couchdb.Server('http://localhost:5984')
#db = couch['melb_tweets']

path = "./st.txt"

def getTimeline(screenName):
    alltweets = []
    try:
        tweets = api.user_timeline(screen_name=screenName, count=200)
        ############ get all the tweets##################
        # new_tweets = api.user_timeline(screen_name=screenName, count=200)
        # alltweets.extend(new_tweets)
        # oldest = alltweets[-1].id - 1
        
        # #keep grabbing tweets until there are no tweets left to grab
        # while len(new_tweets) > 0:
        #     new_tweets = api.user_timeline(screen_name=screenName, count=200, max_id=oldest)
        #     alltweets.extend(new_tweets)
        #     oldest = alltweets[-1].id - 1
    except Exception as e:
        print ("getTimeline", e)
        pass
    return tweets

if __name__ == '__main__':
    keywords = getWords('/Users/sunshine/Desktop/topfastfood.txt')
    bigT = tweepy.Cursor(api.search, result_type='recent',include_entities=True, geocode="-37.8375587,145.0413208,200km").items()
    print access_token
    print access_secret

    while True:
        try:
            tweet = bigT.next()
            with open('data.txt', 'a') as outfile:
                json.dump(tweet._json, outfile)
                outfile.write("\n")
            if tweet._json["coordinates"] != None:
                screenName = tweet._json["user"]["screen_name"]
                alltweets = getTimeline(screenName)
                count = 0
                for tweet in alltweets:
                    count = count + 1
                    overall_count += 1
                    if (tweet._json['coordinates'] != None):
                        coordinates0 = tweet._json['coordinates']['coordinates'][0]
                        coordinates1 = tweet._json['coordinates']['coordinates'][1]
                    else:
                        coordinates0 = 0
                        coordinates1 = 0

                    if tweet._json['place'] != None:
                        placeFullName = tweet._json['place']['full_name']
                    else:
                        placeFullName = None
                    if (coordinates0 > 140.95) & (coordinates0 < 148.63) & (coordinates1 > -39.18) & (coordinates1 < -34) | (placeFullName == 'Melbourne, Victoria'):
                        commonWords = containKeywords(tweet._json["text"], keywords)
                        print commonWords
                        with open('data.txt', 'a') as outfile:
                            json.dump(tweet._json, outfile)
                            outfile.write("\n")
                    #print tweet._json
                print ("The count of tweets for a timeline is: ", count, overall_count)
                if overall_count > 10000:
                    couch.write_to_couch()
                    count = 0
                    overall_count = 0
                # getTimeline(screenName,db)
        except tweepy.TweepError:
            count_error = count_error + 1
            list_id = count_error%4

            access_token = access_token_list[list_id]
            access_secret = access_secret_list[list_id]
            consumer_key = consumer_key_list[list_id]
            consumer_secret = consumer_secret_list[list_id]

            couch.write_to_couch()
            count = 0
            overall_count = 0
            time.sleep(120)
            continue
        except StopIteration:
            break

