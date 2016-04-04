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
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
from textblob import TextBlob
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import googlemaps


access_token = "3254357972-gQDabKOQfbZJsSGyUVynYqckImVjizBDydjuxhX"
access_secret = "rrGORFp6LW3MznoFKfCvkjNo3pAfpVPGb75Vv3rzv4xFF"
consumer_key = "WdTNeWnGBzRHfuJGBN0xoCJxp"
consumer_secret = "1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe"

# consumer_key = "CwP9jWveyzDUC61XFb9iQTlfx";
# consumer_secret = "yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI";
# access_token = "1615559564-AXla3P6ErZuZJCYiWma0S6EoazOAF9LpHS7Zgk6";
# access_secret = "2QgYQdsHdwJ5fzGgmpxDNmfHq3Yh72CCSol2psY"


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
gmaps = googlemaps.Client(key='AIzaSyDeIQ2brFZT6RAL2MULaQJaAelTaWDTxdc')

couch = couchdb.Server()
couch = couchdb.Server('http://localhost:5984')


def save_tweet(tweet):
	#attemt to encode an Object into JSON
	pickled = jsonpickle.encode(tweet)
	results = json.loads(pickled)
	doc = results['py/state']['_json']
	
	# add sentiment value to the tweet
	blob = TextBlob(doc['text'])
	sentiment_polarity = blob.sentiment.polarity
	sentiment_subjectivity = blob.sentiment.subjectivity

	# create a nested json for sentiment score for the tweet
	sentiment_score = {}
	sentiment_score['polarity'] = sentiment_polarity
	sentiment_score['subjectivity'] = sentiment_subjectivity
	doc['sentiment_score'] = sentiment_score
	
	if (doc['coordinates'] != None):
		coordinates0 = doc['coordinates']['coordinates'][0]
		coordinates1 = doc['coordinates']['coordinates'][1]
	else:
		coordinates0 = 0
		coordinates1 = 1

	if doc['place'] != None:
		placeFullName = doc['place']['full_name']
	else:
		placeFullName = None

	if (coordinates0 > 140.95) & (coordinates0 < 148.63) & (coordinates1 > -39.18) & (coordinates1 < -34) | (placeFullName == 'Melbourne, Victoria'):
       	 with open('data.txt', 'a') as outfile:
       	 	print("doc: ", doc)
       	 	print("sentiment_polarity: ", doc['sentiment_score']['polarity'])
        	print("sentiment_score:", doc['sentiment_score']['subjectivity'])
        	json.dump(doc, outfile)
        	outfile.write("\n")
	# store tweets to couchbase

class MyListener(StreamListener):
 
	def on_status(self, status):
		if status._json["coordinates"] != None:
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
