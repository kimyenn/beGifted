import pandas as pd
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem.snowball import SnowballStemmer

'''
nltk.sentiment.vader is used because it takes into consideration special case idioms, capitalization, punctuation, and deals specifically with social media texts

VADER (Valence Aware Dictionary and sEntiment Reasoner)

source code: http://www.nltk.org/_modules/nltk/sentiment/vader.html

Github: https://github.com/cjhutto/vaderSentiment

VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text
(by C.J. Hutto and Eric Gilbert)
Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.  http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf
'''


def remove_links(words):
    if 'http' in words:
        return re.sub('([^0-9A-Za-z \t])|(\w+:\/\/\S+)', '', words)
    return words


def remove_punctuation(sent):
    sent = unicode(sent)
    snowball = SnowballStemmer('english')
    translation_table = dict.fromkeys(map(ord, ')(][:.",!#&;$?'), None)
    return ' '.join([snowball.stem(word) for word in sent.translate(translation_table).split()])


# after stemming
def remove_irrelevant_terms(words):
    return re.sub('\\bsorri\\b|\\bpleas\\b|\\bthank\\b|\\nthx\\b|\\bhi\\b|\\bfave\\b|\\bdm\\b|\\bamp\\b', '', words)


def clean_df(user_df):
    user_df['simple_text'] = user_df['text'].apply(lambda x: remove_links(x))

    #A warning will appear if Twython is not installed
    sid = SentimentIntensityAnalyzer()
    user_df['sentiment'] = user_df['text'].apply(lambda x: sid.polarity_scores(x))

    #keep only fairly positive tweets
    pos_user_tweets = user_df[user_df['sentiment'].apply(lambda x: x['neg']) < .45]

    pos_user_tweets['stemmed_text'] = pos_user_tweets['simple_text'].apply(lambda tweet: remove_punctuation(tweet))

    pos_user_tweets['stripped_text'] = pos_user_tweets['stemmed_text'].apply(lambda tweet: remove_irrelevant_terms(tweet))
    return pos_user_tweets


def user_doc(pos_df):
    return ' '.join([text for text in pos_df['stemmed_text'].values])
