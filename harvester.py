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

import couch
from math import radians, cos, sin, asin, sqrt

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

def getDistance(lon1, lat1, lon2, lat2):

    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    R = 6373 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = R * c
    return km

def readQuery(path):
    a = []
    with open(path, 'r') as f:
        for line in f.readlines():
            a.append(line.strip())

    return a

path = "./st.txt"

def userAllTweet(screenName):
    alltweets = []
    try:
        new_tweets = api.user_timeline(screen_name=screenName, count=200)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            new_tweets = api.user_timeline(screen_name=screenName, count=200, max_id=oldest)
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
    except Exception as e:
        print ("userAllTweet", e)
        pass

    return alltweets


def getTimeline(screenName):
    t = tweepy.Cursor(api.user_timeline, id=screenName,count=200).items()
    # while True:
    try:
        tweet = t.next()
        if (tweet._json["coordinates"] != None) :
        # & (tweet._json['place']['attributes']!= None):
          latitude = tweet._json["coordinates"]["coordinates"][1]
          longitude = tweet._json["coordinates"]["coordinates"][0]
          #restrict to the Melbourne area
          if (longitude > 140.95) & (longitude < 148.63) & (latitude > -39.18) & (latitude < -34) | (tweet._json['place']['full_name'] == 'Melbourne, Victoria'):

                #     if tweet.id_str not in db:

                # db[tweet.id_str] = tweet._json
                # f = open("data.txt", "a+")
                # f.write(tweet._json)
                # f.write("\n")
                with open('data.txt', 'a') as outfile:
                    # outfile.write("\n")
                    # outfile.write(tweet._json)
                    # outfile.write(tweet._json + "\n")
                    json.dump(tweet._json, outfile)
                    outfile.write("\n")
                print tweet._json
                overall_count += 1
    except tweepy.TweepError:
        time.sleep(60)
        # continue
    # except StopIteration:
    #     break

#for i in readQuery(path):
#    stadiumCoordinates = i +','+'2km'
if __name__ == '__main__':
    bigT = tweepy.Cursor(api.search, result_type='recent',include_entities=True, geocode="-37.8375587,145.0413208,200km").items()
    print access_token
    print access_secret

    while True:
        try:
            tweet = bigT.next()
            with open('data.txt', 'a') as outfile:
                json.dump(tweet._json, outfile)
                outfile.write("\n")
            #print tweet._json

            if tweet._json["coordinates"] != None:
                screenName = tweet._json["user"]["screen_name"]
                alltweets = userAllTweet(screenName)
                count = 0
                for tweet in alltweets:
                    count = count + 1
                    overall_count += 1
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

