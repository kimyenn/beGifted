from flask import Flask, render_template, request
app = Flask(__name__)

import os
import sys
import imp
import pandas as pd
import cPickle as pickle
import clean_user_tweets
CWD = os.path.abspath(os.path.dirname(__file__))
sys.path.append(CWD+'/../../code')
#twitter_scrape = imp.load_source('twitter_scrape', CWD+'/../../code/get_tweet_history.py')
from get_tweet_history import twitter_scrape

# home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter')
def twitter():
    return render_template('twitter.html')

@app.route('/twitter_predictions', methods=['POST'])
def twitter_predictions():

    screen_name = request.form['t']
    # twitter_scrape(screen_name)

    user_tweets = pd.read_json('../data/%s_tweets.json' % screen_name)

    #clean user Tweets, perform sentiment analysis, create user document
    user_tweets = clean_user_tweets.clean_df(user_tweets)
    user_doc = clean_user_tweets.user_doc(user_tweets)
    X = vectorizer.transform(user_doc)
    pred = OvR.predict(X)

    return render_template('twitter_predictions.html', predict = pred[0])

if __name__ == '__main__':

    with open('../data/vectorizer.pkl') as f:
        vectorizer = pickle.load(f)
    with open('../data/OvR.pkl') as f:
        OvR = pickle.load(f)
    #
    # with open('../data/cv.pkl') as f:
    #     cv = pickle.load(f)
    # with open('../data/MultiNB.pkl') as f:
    #     MultiNB = pickle.load(f)

    app.run(host='0.0.0.0', port=8080, debug=True)
