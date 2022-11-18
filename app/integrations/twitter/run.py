import os
from app.parser import get_parsed_args
from typing import cast

from dotenv import load_dotenv
from tweepy import Client

from .utils import get_all_tweets, render_to_console

load_dotenv()
ARGS = get_parsed_args()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_HOURS_AGO = cast(int, (os.getenv("TWITTER_HOURS_AGO")))


def render_twitter_results():
    # instantiate client
    twitter_client = Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_KEY_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    )

    # setup render data
    hours_ago = int(ARGS.twitter_hours_ago or TWITTER_HOURS_AGO)
    all_tweets = get_all_tweets(
        client=twitter_client, parsed_args=ARGS, hours_ago=hours_ago
    )

    render_to_console(all_tweets)
