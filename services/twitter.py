import csv
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

files = os.listdir('output')
tweet_len = 0

class Twitterbot:
 
    def __init__(self, email, password):
 
        """Constructor
 
        Arguments:
            email {string} -- registered twitter email
            password {string} -- password for the twitter account
        """
 
        self.email = email
        self.password = password
        options = Options()
        options.headless = False
        fp = webdriver.FirefoxProfile('/Users/davidmarcos/Library/Application Support/Firefox/Profiles/q5rsbubm.David/')

        self.bot = webdriver.Firefox(
            fp,
            options=options,
            executable_path = '/usr/local/bin/geckodriver'
        )

    def get(self, url):
        self.bot.get(url)
 
    def login(self):
        """
            Method for signing in the user
            with the provided email and password.
        """
 
        bot = self.bot
        bot.get('https://twitter.com/login')
        time.sleep(3)
 
        email = bot.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input'
        )
        email.send_keys(self.email)
        email.send_keys(Keys.RETURN)
        time.sleep(2)

        password = bot.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'
        )
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)
        time.sleep(2)

def get_credentials() -> dict:
    # dictionary for storing credentials
    credentials = dict()
    # reading the text file
    # for credentials
    with open('credentials.txt') as f:
        # iterating over the lines
        for line in f.readlines():
            try:
                # fetching email and password
                key, value = line.split(": ")
            except ValueError:
                # raises error when email and password not supplied
                print('Add your email and password in credentials file')
                exit(0)
            # removing trailing
            # white space and new line
            credentials[key] = value.rstrip(" \n")
    # returning the dictionary containing the credentials
    return credentials


def get_tweet_retweeters(user: str, tweet_id: int, idx: int, bot):
    output = []
    bot.get(f"https://twitter.com/{user}/status/{tweet_id}/retweets")
    print(f"Getting retweets for tweet {idx + 1}/{tweet_len}")
    time.sleep(2)
    try:
        retweets_list = bot.bot.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/section/div/div')
    except e:
        print(str(e))
        return output
    retweet = retweets_list.find_element_by_tag_name('div')
    while retweet:
        output.append(retweet.text.split('\n')[:2][-1])
        bot.bot.execute_script("return arguments[0].remove();", retweet)
        try:
            retweet = retweets_list.find_element_by_tag_name('div')
        except:
            break
    json.dump(output, open(f"output/retweets_{tweet_id}.json", "w"), ensure_ascii=False, indent=4)
    return output

credentials = get_credentials()
def init_bot():
    bot = Twitterbot(credentials['email'], credentials['password'])
    # bot.login()
    return bot

def get_tweets_retweeters(tweets, login=False):
    print(tweets)
    output = {}
    credentials = get_credentials()
    bot = Twitterbot(credentials['email'], credentials['password'])
    if login: bot.login()

    for index, tweet in enumerate(tweets):
        print(f"Getting retweets for tweet {index + 1} of {len(tweets)}")
        if len(output) > 10:
            json.dump(output, open(f"output/retweets_{int(datetime.now().timestamp())}.json", "w"), ensure_ascii=False, indent=4)
            output = {}
        rts = get_tweet_retweeters(tweet[1], tweet[0], bot)
        if rts:
            output[tweet[0]] = rts
    json.dump(output, open(f"output/retweets_{int(datetime.now().timestamp())}.json", "w"), ensure_ascii=False, indent=4)

    bot.bot.close()
    return output

workers = 1

def set_up_threads(tweets):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return executor.map(
            get_tweet_retweeters,    
            ["twitter" for tweet in tweets],
            [tweet for tweet in tweets],
            [index for index, tweet in enumerate(tweets)],
            bots * int((len(tweets) / workers)),
            timeout = None
        )
print("Creating bots...")
bots = [init_bot() for i in range(workers)]

print("Getting tweets...")
tweets = json.load(open('output/valid_tweets.json', 'r'))
tweet_len = len(tweets)
retweets = set_up_threads(tweets)

for bot in bots:
    bot.bot.close()
