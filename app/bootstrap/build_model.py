import cPickle as pickle
import pymongo
import pandas as pd
import re
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
# from collections import defaultdict
from sklearn.multiclass import OneVsRestClassifier
from nltk.stem.snowball import SnowballStemmer

def remove_links_and_tags(words):
    if ('http' in words or '@' in words):
        return re.sub('(RT)|(RT @[_A-Za-z0-9]+)|(@[_A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', '', words)
    return words

def remove_links(words):
    if 'http' in words:
        return re.sub('([^0-9A-Za-z \t])|(\w+:\/\/\S+)', '', words)
    return words

def remove_punctuation(sent):
    snowball = SnowballStemmer('english')
    translation_table = dict.fromkeys(map(ord, ')(][:.",!#&;$?'), None)
    return ' '.join([snowball.stem(word) for word in sent.translate(translation_table).split()])

# after stemming
def remove_irrelevant_terms(words):
    return re.sub('\\bsorri\\b|\\bpleas\\b|\\bthank\\b|\\nthx\\b|\\bhi\\b|\\bfave\\b|\\bdm\\b|\\bamp\\b', '', words)

def get_company_df():
    '''
    INPUT: None
    OUTPUT: dataframe where columns are ['company', 'text', 'simple_text', 'stemmed_text', stripped_text]

    DESCRIPTION: Retrieves information of all companies in MonoDB and extracts relevant information
    '''

    ### code to read from MongoDB
    mc = MongoClient()
    db = mc.twitter_db
    input_data = db.tweets_by_companies
    data = pd.DataFrame(list(input_data.find()))

    data['company'] = data['user'].apply(lambda x: x['name'])

    # exclude replies which are usually apologies to concerned customers
    data = data[data['in_reply_to_screen_name'].isnull() == True]

    # remove unncessary information
    data['simple_text'] = data['text'].apply(lambda tweet: remove_links_and_tags(tweet))
    data['stemmed_text'] = data['simple_text'].apply(lambda tweet: remove_punctuation(tweet))
    data['stripped_text'] = data['stemmed_text'].apply(lambda tweet: remove_irrelevant_terms(tweet))
    return data

def build_MultinomialNB(company_tweets):
    ### code to build a NB model
    #df = pd.read_csv(open(filename,'rU'), encoding='utf-8', engine='c')

    X = company_tweets['stripped_text']
    y = company_tweets['company']
    count_vectorizer = CountVectorizer(stop_words='english')
    cv = count_vectorizer.fit_transform(X)
    clf = MultinomialNB()
    clf.fit(cv, y)
    return count_vectorizer, clf

def build_OvR_LinearSVC(company_tweets):
    X = company_tweets['stripped_text']
    y = company_tweets['company']
    tfid_vectorizer = TfidfVectorizer(stop_words='english')
    tf = tfid_vectorizer.fit_transform(X)
    OvR = OneVsRestClassifier(LinearSVC())
    OvR.fit(tf, y)
    return tfid_vectorizer, OvR


#ONLY NECESSARY IF FIRST TIME RUNNING MODEL AND NOTHING HAS BEEN PICKLED
if __name__ == '__main__':
    company_tweets = get_company_df()
    vectorizer, OvR = build_OvR_LinearSVC(company_tweets)
    with open('../data/vectorizer.pkl', 'w') as f:
        pickle.dump(vectorizer, f)
    with open('../data/OvR.pkl', 'w') as f:
        pickle.dump(OvR, f)

    # cv, MultiNB = build_MultinomialNB(company_tweets)
    # with open('../data/cv.pkl', 'w') as f:
    #     pickle.dump(cv, f)
    # with open('../data/MultiNB.pkl', 'w') as f:
    #     pickle.dump(MultiNB, f)
