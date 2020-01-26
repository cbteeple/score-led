from twitter_sentiment import TwitterClient
from collections import deque
import time

# Collect the tweets!

# How many past twitter api calls to save
save_num_calls = 4
num_tweets = 400
call_rate = 15  # seconds

team1 = 'NE'
team2 = 'PHI'

tags = {
    team1: '@Patriots',
    team2: '@Eagles'
}

# Keep an array of the # of tweets sentiment
# [ positive, negative, neutral ]
tweet_sentiment = {
    team1: deque([]),
    team2: deque([])
}

# creating object of TwitterClient Class
api = TwitterClient()

def new_analysis(tag):
    # calling function to get tweets
    tweets = api.get_tweets(query = tag, count = num_tweets) 
    # Number of positive tweets from tweets
    pos_tweets = len([tweet for tweet in tweets if tweet['sentiment'] == 'positive'])
    # Number of negative tweets from tweets
    neg_tweets = len([tweet for tweet in tweets if tweet['sentiment'] == 'negative'])
    # Number of neutral tweets
    neut_tweets = len(tweets) - pos_tweets - neg_tweets 

    return pos_tweets, neg_tweets, neut_tweets

def main():
    positivity = {}

    while 1:
        for team, vals in tweet_sentiment.iteritems():
            print team
            new_tweets = new_analysis(tags[team])
            tweet_sentiment[team].append(new_tweets)

            if len(tweet_sentiment[team]) > save_num_calls:
                tweet_sentiment[team].popleft()

            # Get the percentage of positive/negative/neutral tweets in the list
            t_s = tweet_sentiment[team]
            pos = sum([t[0] for t in t_s])
            neg = sum([t[1] for t in t_s])
            neut = sum([t[2] for t in t_s])
            print t_s
            print po
            print neg
            print neut
    
            positivity[team] =  100 * float(pos) / (pos + neg)

            print team + ': ' + str(positivity[team])

        time.sleep(call_rate)

if __name__ == "__main__":
    main()
