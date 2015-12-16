# original code by https://gist.github.com/yanofsky/5436496
#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import os
import json

#Twitter API credentials
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_key = os.getenv("TWITTER_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


def get_all_tweets(screen_name):
	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	#initialize a list to hold all the tweepy Tweets
	alltweets = []

	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)

	#save most recent tweets
	alltweets.extend(new_tweets)

	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1

	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		print "getting tweets before %s" % (oldest)

		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

		#save most recent tweets
		alltweets.extend(new_tweets)

		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1

		print "...%s tweets downloaded so far" % (len(alltweets))

	#transform the tweepy tweets into a 2D array that will populate the csv
	# outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

    # assume there's MongoDB running on the machine, get a connection to it
    conn = MongoClient('localhost', 27017)
    db = conn['twitter_db']
    collection = db['all_tweets']

	# use the cursor to skip the handling of the pagination mechanism
    # http://docs.tweepy.org/en/latest/cursor_tutorial.html
    tweets = tweepy.Cursor(api.user_timeline, screen_name = screen_name).items()
    while True:
        # as long as I still have a tweet to grab
        try:
            data = tweets.next()
        except StopIteration:
            break
        # convert from Python dict-like structure to JSON format
        jsoned_data = json.dumps(data._json)
        tweet = json.loads(jsoned_data)
        # insert the information in the database
        collection.insert(tweet)

	# #write the csv
	# with open('%s_tweets.csv' % screen_name, 'wb') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(["id","created_at","text"])
	# 	writer.writerows(outtweets)
	#
	# pass
#
#
# if __name__ == '__main__':
# 	#pass in list of usernames of accounts to download
# 	get_all_tweets(sys.argv[1])
