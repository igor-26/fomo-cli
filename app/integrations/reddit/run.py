import os
from typing import cast

from dotenv import load_dotenv
from praw import Reddit

from app.parser import get_parsed_args

from .utils import filter_subreddits, render_to_console

load_dotenv()
ARGS = get_parsed_args()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
REDDIT_BASE_URL = "https://www.reddit.com"
REDDIT_HOURS_AGO = cast(int, (os.getenv("REDDIT_HOURS_AGO")))


def render_reddit_results():
    # instantiate client
    reddit_client = Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
    )

    # setup render data
    filtered_subreddits = filter_subreddits(
        subreddits=reddit_client.user.subreddits(), parsed_args=ARGS
    )
    hours_ago = int(ARGS.reddit_hours_ago or REDDIT_HOURS_AGO)

    render_to_console(
        subreddits=filtered_subreddits,
        hours_ago=hours_ago,
    )
