# -*- coding: utf-8 -*-
"""
Justin Carter
3/3/2024
Reddit's Top Issues

The purpose of the script below is gather and filter words from the top 1000
posts in political subreddits (r/Conservative, r/liberal, and r/NeutralPolitics)
in order to ascertain the issues currently most important to conservatives,
liberals, and those who identify as politically neutral. 
"""

#import necessary packages
import praw
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import re
from my_credentials import app_client_id, app_client_secret, user_agent #local file

#download aspects of packages as needed
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

#use crednetials to access reddit; replace with your own credentials
app_client_id = app_client_id
app_client_secret = app_client_secret
user_agent = user_agent

reddit = praw.Reddit(client_id=app_client_id,
                     client_secret=app_client_secret,
                     user_agent=user_agent)
 
#get post titles, number of upvotes of posts from 1000 hot posts
#from each subreddit

sort = 'top'
limit = 1000
columns = ['title', 'score']

conservative_submissions = reddit.subreddit('Conservative').hot(limit=limit)
liberal_submissions = reddit.subreddit('Liberal').hot(limit=limit)
neutral_submissions = reddit.subreddit('NeutralPolitics').hot(limit=limit)

conservative_df = pd.DataFrame([[x.title, x.score]for x in conservative_submissions], columns=columns)
liberal_df = pd.DataFrame([[x.title, x.score]for x in liberal_submissions], columns=columns)
neutral_df = pd.DataFrame([[x.title, x.score]for x in neutral_submissions], columns=columns)

conservative_corpus = ' '.join(conservative_df['title'])
liberal_corpus = ' '.join(liberal_df['title'])
neutral_corpus = ' '.join(neutral_df['title'])

def make_noun_dataframe(corpus):
    
    #make function to remove non-nouns
    def remove_non_nouns(word_list):
        tagged_words = nltk.pos_tag(word_list)
        nouns = [word for word, pos in tagged_words if pos.startswith('N')]
        return nouns
    
    words = []
    word = ''
    for thing in corpus:
        if thing == ' ':
            words.append(word)
            word = ''
            continue
        else:
            word += thing

    my_nouns = remove_non_nouns(words)
    my_nouns = [word.title() for word in my_nouns]
    word_counts = Counter(my_nouns)
    
    #sort word counts in descending order, then take the top 30 words
    sorted_word_counts = {word: count for word, count in sorted(word_counts.items(), key=lambda item: item[1], reverse=True)}
    in_words = list(sorted_word_counts.keys())[:30]
    
    filtered_words = [word for word in my_nouns if word in in_words] #check words against in_list
    filtered_words_cleaned = [re.sub(r'[^\w\s]', '', word) for word in filtered_words]
    filtered_words_cleaned = [word for word in filtered_words_cleaned if word != ' ']

    #put list into df, make each element a row, reset index
    nouns_df = pd.DataFrame([{'Nouns':filtered_words_cleaned}]).explode('Nouns').reset_index(drop=True)
    return nouns_df

liberal_nouns_df = make_noun_dataframe(liberal_corpus)
conservative_nouns_df = make_noun_dataframe(conservative_corpus)
neutral_nouns_df = make_noun_dataframe(neutral_corpus)

#Uncomment following lines to save datasets:
    
"""
conservative_nouns_df.to_csv('conservative_nouns_df.csv', header=True, index=False)
liberal_nouns_df.to_csv('liberal_nouns_df.csv', header=True, index=False)
neutral_nouns_df.to_csv('neutral_nouns_df.csv', header=True, index=False)
"""
