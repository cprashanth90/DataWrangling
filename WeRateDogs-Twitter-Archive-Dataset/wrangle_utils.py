
import pandas as pd
import numpy as np
import csv
import json
import requests
import tweepy
import re


def write_json_objects_to_txtfile(list_items,file):
    with open(file,"wb") as out:
        for item in list_items: 
            out.write(bytes(json.dumps(item),encoding="utf-8") + b"\n")

def get_predictions_file(file_url):
    r = requests.get(file_url)
    output_file = file_url.rsplit("/",1)[1]
    output_data = []
    with open(output_file,"wb") as out:
        out.write(r.content)
    
    with open(output_file) as infile:
        reader = csv.DictReader(infile,lineterminator="\n",delimiter="\t")
        for row in reader:
            
            output_data.append(row)
    
    return pd.DataFrame(output_data)

def get_twitter_API():

    consumer_key = input("Please Enter your Consumer Key: \n")
    consumer_secret_key = input("Please Enter your Consumer Secret Key: \n")
    access_token = input("Please Enter your Access Token: \n")
    access_token_secret = input("Please Enter your Access Token Secret: \n")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    return api

def get_tweet_id_from_urls(expanded_url):
    urls = []
    TWEET_PATTERN = "twitter.com/([^/]*)/status/([^/]*)/"
    tweet_id = ""
    if "," in expanded_url:
        urls = expanded_url.split(",")
    else:
        urls.append(expanded_url)
    
    for url in urls:
        if "twitter.com" in url:
            results = re.findall(TWEET_PATTERN,url)
            tweet_id = results[0][1]
            break
    
    return int(tweet_id)


def get_json_obj_from_twitter(api,tweet_id):
    status = None
    try:
        status = api.get_status(tweet_id,tweet_mode="extended",wait_on_rate_limit=True)
    except Exception as e:
        print ("The Tweet ID: {} does not exist in the Twitter API".format(tweet_id))
    return status
        

def get_json_data(api,row):
    
    json_obj = {}
    # First lets try fetching the tweet data from the tweet_id column.
    tweet_id = row["tweet_id"]
    status = get_json_obj_from_twitter(api,tweet_id)
    
    # If this Tweet ID does not exist in the Twitter API, lets try getting the status from the 'retweeted_status_id' field.
    if not status:
        if row["retweeted_status_id"] != -1:
            tweet_id = row["retweeted_status_id"]
            print ("Trying Retweet ID: {}".format(tweet_id))
            status = get_json_obj_from_twitter(api,tweet_id)
    
    # If this doesnt work as well, Attempt fetching status using the 'expanded_urls' field
    if not status:
        expanded_url = row["expanded_urls"]
        tweet_id = get_tweet_id_from_urls(expanded_url)
        print ("Trying Tweet ID from the Media URL: {}".format(tweet_id))
        status = get_json_obj_from_twitter(api,tweet_id)
    
    try:
        json_obj = status._json
    except AttributeError:
        print ("Unable to fetch Tweet IDs")
    
    return(json_obj)
    