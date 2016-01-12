# modified from https://gist.github.com/yanofsky/5436496
# script to download up to <= 3200 (the official API limit) of most recent tweets from a user's timeline and save directly to MongoDB

from pymongo import MongoClient
import tweepy
import json
import os
import re
import time
import csv

#Twitter API credentials
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


def twitter_scrape(screen_name, user=True):
    '''
    Description:

    INPUT: screen_name is a Twitter user to be scraped
    OUTPUT: None, a .json file is created which contains the Tweets
    '''

    # authorize twitter, initialize tweepy
    # make sure to set the corresponding flags as True to whether or
    # not automatically wait for rate limits to replenish

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # initialize a list to hold tweepy tweets
    alltweets = []

    # cannot scrape private users
    if api.get_user(screen_name).protected:
        return "{}'s account is protected".format(screen_name)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    alltweets.extend(new_tweets)

    #save id of the oldest tweet less one for pagination
    oldest = alltweets[-1].id - 1

    while len(new_tweets) > 0:
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1

    if !user:
        # Connect to MongoDB to insert data
        conn = MongoClient('localhost', 27017)
        db = conn['twitter_db']
        collection = db['tweets_by_companies']

    if user:
    # call ._json property for each status to convert to JSON serializable format for MongoDB
        tweets = [status._json for status in alltweets]

        with open('../data/%s_tweets.json' % screen_name, 'w') as outfile:
            json.dump(tweets, outfile)
    #
    # # insert the information in the database if purpose is collecting and saving
    # collection.insert(tweets)
    print "Successfully scraped: {} for {}".format(time.asctime(time.localtime()), screen_name)


def continuous_scraper(name):
    '''
    Helper function to use with a list of screen names. It will run exhaustively through list
    skipping problematic accounts (banned/suspended/etc)
    '''
    try:
        twitter_scrape(name)
    except KeyboardInterrupt:
        print "KeyboardInterrupt"
        return
    except:
        print "Error encountered at {} on {}, will try in 5 minutes".format(time.asctime(time.localtime()), name)
        time.sleep(300)
        return

#add in __name__ == '__main__'
