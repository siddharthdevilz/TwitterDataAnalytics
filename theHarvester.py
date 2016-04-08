import tweepy
import sys
import jsonpickle
import os
import random
from textblob import TextBlob
import couch
import json

# Replace the API_KEY and API_SECRET with your application's key and secret.

apikey1 = { 'consumer_key' : "WdTNeWnGBzRHfuJGBN0xoCJxp",
			'consumer_secret' : "1BKrrH5eQFrYzzzf6Z5bXYdfVNENtoDpdXWVQw0NDt5TK6Czoe"}

apikey2 = { 'consumer_key' : "7CQ1IAImnhdjQ5Tj8eB83LdMj",
			'consumer_secret' : "CqXHoVEAcW5XINRqtVLDV7AkOzFmmFg8SUUQrnRJVjqP8ZzLMU"}

apikey3 = { 'consumer_key' : "CwP9jWveyzDUC61XFb9iQTlfx",
			'consumer_secret' : "yLDl387DdORqvXaFEyxOPR9MVEjYTQeIUFwMRJQu5NIrlgnfRI"}

apikey4 = { 'consumer_key' : "5BVhllWNmmKj6BkFZbO2lBYD9",
			'consumer_secret' : "xd80Q3dWvEBNBZtjGrikFZXJnavWjEEnTf5fFLOgwXlb9AuRwp"}

apikeys = [apikey1, apikey2, apikey3, apikey4]

centre_list = [[-37.740313, 144.759292], [-37.871059, 145.151023], [-37.606616, 145.079269]]

RADIUS = "20km"

key = random.choice(apikeys)
auth = tweepy.AppAuthHandler(key['consumer_key'], key['consumer_secret'])
api = tweepy.API(auth) #, wait_on_rate_limit=True,
				   #wait_on_rate_limit_notify=True)
 
if (not api):
	print ("Can't Authenticate")
	sys.exit(-1)

#searchQuery = '#someHashtag'  # this is what we're searching for
maxTweets = 10000000 # Some arbitrary large number
tweetsPerQry = 100  # this is the max the API permits
fName = 'tweets.txt' # We'll store the tweets in a text file.


# If results from a specific ID onwards are reqd, set since_id to that ID.
# else default to no lower limit, go as far back as API allows
sinceId = None

# If results only below a specific ID are, set max_id to that ID.
# else default to no upper limit, start from the most recent tweet matching the search query.
max_id = -1L

tweetCount = 0

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
	#global error_rate_count
	#while True:
	try:
		#tweet = tweets.next()
		for tweet in new_tweets:
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

			
			# getTimeline(screenName,db)
	except Exception, e:
		print(e)



print("Downloading max {0} tweets".format(maxTweets))

geo = str(centre_list[0][0])+","+str(centre_list[0][1])+","+RADIUS

if __name__ == '__main__':
	iteration_count = 0
	while tweetCount < maxTweets:
		try:
			if (max_id <= 0):
				if (not sinceId):
					new_tweets = api.search(geocode=geo, rpp=tweetsPerQry)
				else:
					new_tweets = api.search(geocode=geo, rpp=tweetsPerQry,
											since_id=sinceId)
			else:
				if (not sinceId):
					new_tweets = api.search(geocode=geo, rpp=tweetsPerQry,
											max_id=str(max_id - 1))
				else:
					new_tweets = api.search(geocode=geo, rpp=tweetsPerQry,
											max_id=str(max_id - 1),
											since_id=sinceId)
			if not new_tweets:
				print("No more tweets found")
				break

			save_tweet(new_tweets)



			# for tweet in new_tweets:
			#     f.write(jsonpickle.encode(tweet._json, unpicklable=False) +
			#             '\n')
			tweetCount += len(new_tweets)
			iteration_count += len(new_tweets)
			if iteration_count > 500:
					couch.write_to_couch()
					iteration_count = 0

			print("Downloaded {0} tweets".format(tweetCount))
			max_id = new_tweets[-1].id
		except tweepy.TweepError as e:
			# Just exit if any error
			print("some error : " + str(e))
			key = random.choice(apikeys)
			auth = tweepy.AppAuthHandler(key['consumer_key'], key['consumer_secret'])
			api = tweepy.API(auth)
			#break

print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))