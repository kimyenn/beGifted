# modified from https://gist.github.com/yanofsky/5436496
# script to download up to <= 3200 (the official API limit) of most recent tweets from a user's timeline and save directly to MongoDB
from pymongo import MongoClient

import tweepy
import json
import os
import time

#Twitter API credentials
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


def twitter_scrape(screen_name):
	#authorize twitter, initialize tweepy
    # make sure to set the corresponding flags as True to whether or
    # not automatically wait for rate limits to replenish

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # assuming there's MongoDB running on the machine, get a connection to it
	conn = MongoClient('localhost', 27017)
	db = conn['twitter_db']
	collection = db['tweets_by_users']

    #initialize a list to hold tweepy tweets
	alltweets = []

	if api.get_user(screen_name).protected:
		return
	new_tweets = api.user_timeline(screen_name=screen_name, count=200)

	alltweets.extend(new_tweets)

    #save id of the oldest tweet less one for pagination
	oldest = alltweets[-1].id - 1

	while len(new_tweets) > 0:
		new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

		alltweets.extend(new_tweets)

		oldest = alltweets[-1].id - 1

    # call ._json property for each status to convert to JSON serializable format for MongoDB
	tweets = [status._json for status in alltweets]
	collection.insert(tweets)
	# insert the information in the database

	print "Successfully scraped: {}".format(screen_name)

#helper function to catch errors (unless interrupted by user) and rerun in 15 minutes
def restart(name):
	try:
		twitter_scrape(name)
	except KeyboardInterrupt:
		print "KeyboardInterrupt"
		return _scra
	except:
		print "Error encountered at {}, will try in 15 minutes".format(name)
		time.sleep(900)
		twitter_scrape(name)
