import tweepy
import time
#import couchdb
import os
import random
import urllib
import json
from tweepy import Stream
from tweepy.streaming import StreamListener
#import simplejson
import datetime
from datetime import timedelta
import math
from textblob import TextBlob
#from geopy.geocoders import Nominatim
import couch

centre_list = [[-37.740313, 144.759292], [-37.871059, 145.151023], [-37.606616, 145.079269]]

apikey1 = { 'access_token' : "3254357972-gQDabKOQfbZJsSGyUVynYqckImVjizBDydjuxhX",
            'access_secret' : "rrGORFp6LW3MznoFKfCvkjNo3pAfpVPGb75Vv3rzv4xFF",
            'consumer_key' : "WdTNeWnGBzRHfuJGBN0xoCJxp",
            'consumer_secret' : "1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe"}

apikey2 = { 'access_token' : "2787646230-a4sEVXjIlHU8rslO2jpsf2lX2ksyOVQEm40VZrE",
            'access_secret' : "Cnb2Z3t83Iow5r6qCOldFsTSHDBM8nzP37RWWsd1sy9fW",
            'consumer_key' : "7CQ1IAImnhdjQ5Tj8eB83LdMj",
            'consumer_secret' : "CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU"}

apikey3 = { 'access_token' : "1615559564-AXla3P6ErZuZJCYiWma0S6EoazOAF9LpHS7Zgk6",
            'access_secret' : "2QgYfYnTkkQdsHdwJ5fzGgmpxDNmfHq3Yh72CCSol2psY",
            'consumer_key' : "CwP9jWveyzDUC61XFb9iQTlfx",
            'consumer_secret' : "yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI"}

apikey4 = { 'access_token' : "705196484359159808-mdR84YBpYoQNWb5j9NKAP5RoEhrEHky",
            'access_secret' : "tgLkR7CsubtPMeRJvmMVit5AvrE2szZz6TgegJeKJMGp3",
            'consumer_key' : "5BVhllWNmmKj6BkFZbO2lBYD9",
            'consumer_secret' : "xd80Q3dWvEBNBZtjGrikFZXJnavWjEEnTf5fFLOgwXlb9AuRwp"}

apikeys = [apikey1, apikey2, apikey3, apikey4]

# access_token_list = ['3254357972-gQDabKOQfbZJsSGyUVynYqckImVjizBDydjuxhX', '2787646230-a4sEVXjIlHU8rslO2jpsf2lX2ksyOVQEm40VZrE', '1615559564-AXla3P6ErZuZJCYiWma0S6EoazOAF9LpHS7Zgk6']
# access_secret_list = ['rrGORFp6LW3MznoFKfCvkjNo3pAfpVPGb75Vv3rzv4xFF', 'CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU', 'yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI']
# consumer_key_list = ['WdTNeWnGBzRHfuJGBN0xoCJxp', '7CQ1IAImnhdjQ5Tj8eB83LdMj', 'CwP9jWveyzDUC61XFb9iQTlfx']
# consumer_secret_list = ['1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe', 'CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU', 'yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI']

count_error = 0
error_rate_count = 0




#couch = couchdb.Server()
#couch = couchdb.Server('http://localhost:5984')
#db = couch['melb_tweets']

path = "./st.txt"

def getTimeline(screenName):
    alltweets = []
    tweets = ''
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
    overall_count = 0
    while True:
        try:
            tweet = tweets.next()
            if tweet._json["coordinates"] != None:
                # screenName = tweet._json["user"]["screen_name"]
                # alltweets = getTimeline(screenName)
                count = 0
                if check_location(tweet._json) == True:
                    tweet._json = add_sentiment_score(tweet._json)
                    count = count + 1
                    overall_count = overall_count + 1
                    with open('data.txt', 'a') as outfile:
                        json.dump(tweet._json, outfile)
                        outfile.write("\n")
                        # print(tweet._json)
                        # print("sentiment_polarity: ", tweet._json['sentiment_score']['polarity'])
                        # print("sentiment_score:", tweet._json['sentiment_score']['subjectivity'])

                # for tweet in alltweets:
                #     count = count + 1
                #     overall_count = overall_count + 1
                #     if check_location(tweet._json) == True:
                #         with open('data.txt', 'a') as outfile:
                #             json.dump(tweet._json, outfile)
                #             outfile.write("\n")
                #             print(tweet._json)ba

                # print ("The count of tweets for a timeline is: ", count, overall_count)

                if overall_count > 250:
                    couch.write_to_couch()
                    count = 0
                    overall_count = 0
                # getTimeline(screenName,db)
        except tweepy.TweepError:
            error_rate_count += 1
            if(error_rate_count <= 3):
                key = random.choice(apikeys)
                print("Changed apikey")
                print(key)
                auth = tweepy.OAuthHandler(key['consumer_key'], key['consumer_secret'])
                auth.set_access_token(key['access_token'], key['access_secret'])
                api = tweepy.API(auth)
            else:
                time.sleep(120)
                print("Sleeping....")
                error_rate_count = 0
       # except Exception, e:
        #    print e
            # count_error = count_error + 1
            # list_id = count_error%4

            # access_token = access_token_list[list_id]
            # access_secret = access_secret_list[list_id]
            # consumer_key = consumer_key_list[list_id]
            # consumer_secret = consumer_secret_list[list_id]

            # couch.write_to_couch()
            # count = 0
            # overall_count = 0
            # time.sleep(120)
            continue
        except StopIteration:
            break

if __name__ == '__main__':

    key = random.choice(apikeys)
    auth = tweepy.OAuthHandler(key['consumer_key'], key['consumer_secret'])
    auth.set_access_token(key['access_token'], key['access_secret'])
    api = tweepy.API(auth)

    geocode_co = str(centre_list[0][0])+","+str(centre_list[0][1])+","+"19.5km"

    error_rate_count = 0
    try:
        tweets = tweepy.Cursor(api.search, result_type='recent',include_entities=True, geocode=geocode_co).items()
        error_rate_count = 0
        save_tweet(tweets)
    except tweepy.TweepError:
        error_rate_count += 1
        if(error_rate_count <= 3):
            key = random.choice(apikeys)
            print("Changed apikey")
            print(key)
            auth = tweepy.OAuthHandler(key['consumer_key'], key['consumer_secret'])
            auth.set_access_token(key['access_token'], key['access_secret'])
            api = tweepy.API(auth)
        else:
            time.sleep(120)
            print("Sleeping....")




