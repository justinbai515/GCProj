import tweepy
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from textblob import TextBlob
from wordcloud import WordCloud
from collections import Counter
from twitterKeys import getKeys

#call for access/authorization keys for the Twitter APIs in a separate file containing the keys
consumerKey = getKeys(0)
consumerSecretKey = getKeys(1)
accessToken = getKeys(2)
accessSecretToken = getKeys(3)

#methods to access Twitter APIs and check valid keys
authenticate = tweepy.OAuthHandler(consumerKey, consumerSecretKey)
authenticate.set_access_token(accessToken, accessSecretToken)
api = tweepy.API(authenticate, wait_on_rate_limit = True)

#function to grab tweets from API; 'extended' accounts for tweets that were made after update to 280 from 140 characters
def getRegPosts(twit_name, num):
    timeline = api.user_timeline(screen_name = twit_name, count = num, lang = 'en', tweet_mode = "extended")
    arr = [] 
    for i in timeline[:num]:
        arr.append(i.full_text)
    return arr

#same as previous function, except is used for instances of hashtags in posts
def getHashtagPosts(hashtag, num, date = None):
    timeline = list(api.search(hashtag, count = num, lang = 'en', tweet_mode = "extended"))
    arr = []
    for i in timeline[:-1]:
        arr.append(i.full_text)
    return arr

#gets rid of usernames of twitter user, URLs, and other miscellaneous strings by substituting characters with an empty string
def clean(text):
    text = re.sub('@[A-Za-z0–9]+', '', text) 
    text = re.sub('RT[\s]+', '', text) 
    text = re.sub('https?:\/\/\S+', '', text)
 
    return text

#creates list of sentiments in numerical form
def getPol(df, col = 'Tweets'):
    arr = []
    for i in df[col]:
        arr.append(TextBlob(i).sentiment.polarity)
    return arr

#determines tweet to be negative, positive, or neutral by taking 'score' of tweet and comparing to 0 
def analysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

#returns data frame of analyzed sentiments/polarities
def getSentiment(target, num, date = None):
    if target[0] == '#':
        arr = getHashtagPosts(target, num, date)
        frame = pd.DataFrame(arr, columns = ['Tweets'])
        cleaned = frame['Tweets'].apply(clean)
        cleaned  = cleaned.to_frame()
        cleaned['Polarity'] = getPol(cleaned, 'Tweets')
        cleaned['Outcome'] = cleaned['Polarity'].apply(analysis)
    else:
        arr = getRegPosts(target, num)
        frame = pd.DataFrame(arr, columns = ['Tweets'])
        cleaned = frame['Tweets'].apply(clean)
        cleaned  = cleaned.to_frame()
        cleaned['Polarity'] = getPol(cleaned, 'Tweets')
        cleaned['Outcome'] = cleaned['Polarity'].apply(analysis)
    return cleaned

def sortdf(dataframe, sorter = 'Polarity', order = False):
    return dataframe.sort_values(by=[sorter], ascending = order )

#credits to Elliot Rubin for helping us understand how to write the last two functions and the 'clean' function

#function for returning proportions of analysis in the form of percentages
def func(pct, allValues): 
    absolute = int(pct / 100.*np.sum(allValues)) 
    return "{:.1f}%\n({:d} Tweets)".format(pct, absolute) 


check = 0
font = {'size': 18, 'color': '#0E0B4A'}
wp = { 'linewidth' : 1, 'edgecolor' : "green" }
colors = ('#484bf7', '#ffa600', '#ff007e') 
explode = (0.1, 0.0, 0.25)
sentiments = ['Positive', 'Neutral', 'Negative']

while check == 0:
    userSearch = input('What hashtag would you like to analyze from Twitter(something broad like Covid19)? #')
    df = getSentiment(('#' + userSearch), 1000)
    data = df['Outcome'].value_counts()
    y_pos = np.arange(len(data))    

    fig, ax = plt.subplots(figsize =(10, 7)) 
    wedges, texts, autotexts = ax.pie(data,  autopct = lambda pct: func(pct, data), explode = explode,  labels = sentiments, 
                                    shadow = True, colors = colors, startangle = 0, wedgeprops = wp, textprops = dict(color ="black")) 
    ax.legend(wedges, sentiments, title ="Sentiments", loc = 'upper left', bbox_to_anchor =(1, 0, 0.5, 1)) 

    plt.setp(autotexts, size = 8, weight = "bold") 
    ax.set_title("Proportions of General Sentiments in Sample Tweets Towards " + userSearch.capitalize()) 
    plt.show()

    

    fig2, ax2 = plt.subplots(figsize =(10, 7)) 
    bars, texts, autotexts = ax2.bar(y_pos, data, color = colors, edgecolor = 'green')
    plt.title('General Sentiments of Sample Tweets Towards ' + userSearch.capitalize() + ' as a Bar Graph')
    plt.xticks(y_pos, sentiments)
    plt.ylabel('Number of Tweets', fontdict = font)
    plt.xlabel('Sentiments', fontdict = font)
    plt.show()

    if input('Would you like to analyze anything else (Yes/No)? ').capitalize() == 'No':
        check = 1

print('Thank you for looking at our project!')
        
