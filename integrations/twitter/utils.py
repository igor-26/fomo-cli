import os
from argparse import Namespace
from datetime import datetime, timedelta
from textwrap import dedent
from typing import Tuple, cast

import pytz
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import track as rich_track
from tweepy import Client
from tweepy.client import Response
from tweepy.tweet import Tweet
from tweepy.user import User

load_dotenv()
console = Console()
_TIMEZONE = cast(str, os.getenv("_TIMEZONE"))


def get_current_user_following(client: Client, parsed_args: Namespace) -> list[User]:
    """Returns a list of followed users checked against `--twitter-include` and `--twitter-exclude` flags"""

    include_users_arg = parsed_args.twitter_include
    exclude_users_arg = parsed_args.twitter_exclude

    me_id = client.get_me().data["id"]
    users = client.get_users_following(id=me_id, user_auth=True).data

    if include_users_arg:
        return [s for s in users if s.username.lower() in include_users_arg]

    if exclude_users_arg:
        return [s for s in users if s.username.lower() not in exclude_users_arg]

    return list(users)


def get_excluded_tweet_types(exclude_list: list, parsed_args: Namespace) -> list | None:
    """Returns a list of excluded tweet types or None if no args are passed in"""

    include_retweets_arg = parsed_args.twitter_retweets
    include_replies_arg = parsed_args.twitter_replies

    if include_replies_arg:
        exclude_list.remove("replies")

    if include_retweets_arg:
        exclude_list.remove("retweets")

    return exclude_list if exclude_list else None


def get_all_tweets(
    client: Client, parsed_args: Namespace, hours_ago: int
) -> list[Response]:
    """Return all tweets(response objects) from followed users checked against `excluded_tweet_types` and `hours_ago`"""

    time_ago = datetime.utcnow() - timedelta(hours=hours_ago)
    following = get_current_user_following(client, parsed_args)

    excluded_tweet_types = get_excluded_tweet_types(
        exclude_list=["replies", "retweets"], parsed_args=parsed_args
    )

    all_tweets = []
    for followed in rich_track(
        following,
        description=f"[bold blue]Twitter[/bold blue] Finding tweets since [bold]{hours_ago}h[/bold] ago",
    ):
        followed_id = followed.data["id"]

        tweets = client.get_users_tweets(
            id=followed_id,
            start_time=time_ago,
            tweet_fields=[
                "created_at",
                "public_metrics",
                "author_id",
            ],
            user_fields=["name", "username", "url"],
            expansions=["author_id"],
            exclude=excluded_tweet_types,
            user_auth=True,
        )

        if not tweets.meta["result_count"]:
            continue

        all_tweets.append(tweets)

    return all_tweets


def get_tweet_type(tweet: Tweet) -> Tuple[str, str]:
    """Returns tuple of tweet type and color representation based on the `tweet["text"]` contents"""

    if tweet["text"].startswith("@"):
        return "reply", "bold blue"

    if tweet["text"].startswith("RT"):
        return "retweet", "bold green"

    return "tweet", "bold red"


def format_tweet(tweet: Tweet, user: User, metrics: dict, _timezone: str) -> str:
    """Returns formatted tweet representation"""

    name = f"[bold]{user['name']}[/bold]"
    username = f"[link=https://twitter.com/{user['username']}]@{user['username']}[/link]"
    created_at = f'{(tweet["created_at"].astimezone(pytz.timezone(_timezone))).strftime("%b %-d %H:%M")} ({_timezone})'
    body = tweet["text"]
    replies = f"💬 {metrics['reply_count']}"
    retweets = f"🔃 {metrics['retweet_count']}"
    likes = f"♥️  {metrics['like_count']}"
    tweet_type, tweet_color = get_tweet_type(tweet)
    link_to_tweet = f"[{tweet_color}][link=https://twitter.com/twitter/status/{tweet['id']}]Go to {tweet_type} →[/link][/{tweet_color}]"

    return dedent(
        f"{name} {username} · {created_at}"
        "\n\n"
        f"{body}"
        "\n\n"
        f"{replies}  {retweets}  {likes}  {link_to_tweet}"
    )


def format_tweet_count(tweets: list[Response]) -> str:
    """Returns formatted representation of tweet count"""

    if not len(tweets):
        return "[red bold]No tweets found.[/red bold]"

    tweet_count = sum([t.meta["result_count"] for t in tweets])

    return (
        f"[green]{tweet_count} new {'tweet' if tweet_count == 1 else 'tweets'}[/green]"
    )


def render_to_console(all_tweets: list[Response]) -> None:
    """Renders processed data to console"""

    tweet_count_text = format_tweet_count(all_tweets)
    console.print(tweet_count_text)

    for tweet_obj in all_tweets:
        users = {u["id"]: u for u in tweet_obj.includes["users"]}

        for tweet in sorted(
            tweet_obj.data, key=lambda tweet: tweet["created_at"], reverse=True
        ):
            user = users[tweet.author_id]
            metrics = tweet["public_metrics"]

            console.print(Panel(format_tweet(tweet, user, metrics, _TIMEZONE)))
