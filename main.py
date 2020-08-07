from configparser import ConfigParser
import tweepy
import time
import requests
import os
import praw
import emoji

file = 'config.ini'
config = ConfigParser()
config.read(file)

def reddit_api(): #handles auth for twitter api
    CLIENT_ID = config['reddit_auth']['CLIENT_ID']
    CLIENT_SECRET = config['reddit_auth']['CLIENT_SECRET']
    USERNAME = config['reddit_auth']['USERNAME']
    PASSWORD = config['reddit_auth']['PASSWORD']
    USER_AGENT = config['reddit_auth']['USER_AGENT']

    reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT,
                     username=USERNAME,
                     password=PASSWORD)
    return reddit

def twitter_api(): #handles auth for twitter api
    API_KEY = config['twitter_auth']['API_KEY']
    API_SECRET = config['twitter_auth']['API_SECRET']
    ACCESS_KEY = config['twitter_auth']['ACCESS_KEY']
    ACCESS_SECRET = config['twitter_auth']['ACCESS_SECRET']

    auth = tweepy.OAuthHandler(API_KEY,API_SECRET)
    auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

def tweet_url_image(url,message): #sends tweet containing image and message using url
    twit_api = twitter_api()
    filename = "temp.jpg"
    request = requests.get(url,stream=True)


    if request.status_code == 200: #uses requests to get image from url
        with open(filename,'wb') as image:
            for chunk in request:
                image.write(chunk)

        try: #handles weird formats that can be download but not uploaded; i.e gfycat
            picture = twit_api.media_upload("temp.jpg")
            twit_api.update_status(status = message,media_ids = [picture.media_id]) #uploads image from with message
            print("Tweet sent.")
        except tweepy.TweepError as err:
            print("TweepyError: Unable to upload image; Tweet skipped")
        os.remove(filename)
    else:
        print("Unable to download image; Tweet skipped")

def post_reddit_to_twitter(curr_sub):
    print(f"\nCurrent sub: {curr_sub.display_name}")
    for submission in curr_sub.hot(limit=5):
        if len(str(submission.title)) < 280 and not submission.stickied : #check if title fits twitter limit and is not a sticky
            print(f"Trying to upload {submission.title}")
            url = submission.url
            title = submission.title.replace('@','') #removes @ to prevent accidental tagging
            title = title.replace('Me',f"u/{str(submission.author)}") #replaces selfpost titles with reddit username
            message = emoji.emojize(f"[ :earth_asia: r/{submission.subreddit.display_name}] \"{title}\" \n :link:: reddit.com{submission.permalink}",use_aliases=True) #generates message formated with emoji
            tweet_url_image(url, message)
            print("Please wait 10 seconds... \n")
            time.sleep(10)

reddit = reddit_api()
print("Bot initialized...")
print("Tweet from single subreddit or multireddit?")
print("Enter 'S' for single subreddit or 'M' for multireddit")
user_input = input()
if user_input == 'S':
    curr_sub = reddit.subreddit(config['reddit_posts']['subreddit'])
    post_reddit_to_twitter(curr_sub)
    print("Uploads are finished.")
elif user_input == 'M':
    curr_sub = reddit.multireddit(config['reddit_posts']['multireddit_curator'],config['reddit_posts']['multireddit_name'])
    post_reddit_to_twitter(curr_sub)
    print("Uploads are finished.")
else:
    print("Input error! Please restart the program and try again")


