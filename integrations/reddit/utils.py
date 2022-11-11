import os
from argparse import Namespace
from datetime import datetime, timedelta
from textwrap import dedent
from typing import Iterator, cast

import pytz
from dotenv import load_dotenv
from praw.models.reddit.submission import Submission
from praw.models.reddit.subreddit import Subreddit
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

load_dotenv()
console = Console()
_TIMEZONE = cast(str, os.getenv("_TIMEZONE"))


def filter_subreddits(
    subreddits: Iterator[Subreddit], parsed_args: Namespace
) -> list[Subreddit]:
    """Returns a list of subreddits checked against `--reddit-include` and `--reddit-exclude` flags"""

    include_arg = parsed_args.reddit_include
    exclude_arg = parsed_args.reddit_exclude

    if include_arg:
        return [s for s in subreddits if s.display_name.lower() in include_arg]
    if exclude_arg:
        return [s for s in subreddits if s.display_name.lower() not in exclude_arg]

    return list(subreddits)


def format_post_count(posts: list[Submission]) -> str:
    """Returns formatted post count"""

    post_count = len(posts)

    if not post_count:
        return "No posts"

    return f"{post_count} new {'post' if post_count == 1 else 'posts'}"


def format_ratio(ratio: float) -> str:
    """Returns formatted ratio representation"""

    ratio_emoji = None
    if ratio >= 0.75:
        ratio_emoji = "😊"
    elif ratio >= 0.5:
        ratio_emoji = "😐"
    elif ratio >= 0.25:
        ratio_emoji = "🙁"
    else:
        ratio_emoji = "😡"

    return f"{ratio_emoji} {round(ratio * 100)}%"


def format_post_hint(post: Submission) -> str:
    """Returns formatted post hint representation"""

    if hasattr(post, "post_hint"):
        post_hint = post.post_hint

        if post_hint == "image":
            return "🖼" + " "

        if post_hint in ["hosted:video", "rich:video"]:
            return "🎥"

    if hasattr(post, "is_gallery"):
        return "Gallery 🖼" + " "

    return "🔗"


def format_post(post: Submission, base_url: str, _timezone: str) -> str:
    """Returns formatted post representation"""

    title = f"{format_post_hint(post)} [green][link={base_url+post.permalink}]{post.title}[/link][/green]"
    ups = f"[red]↑{post.ups}[/red]"
    upvote_ratio = format_ratio(post.upvote_ratio)
    comments = f"💬 {post.num_comments}"
    flair = f"[white]{f' | [red bold]{post.link_flair_text}[/red bold]' if post.link_flair_text else ''}"
    subreddit_info = f"| {post.author} in {post.subreddit_name_prefixed}"
    created_at = f"| [b]{datetime.fromtimestamp(post.created_utc, pytz.timezone(_timezone)).strftime('%b %-d %H:%M')}[/b] ({_timezone})"
    selftext = f"\n{escape(post.selftext)}\n\n" if len(post.selftext) else ""

    return dedent(
        f"{title}"
        "\n"
        f"{selftext}"
        f"{ups}  {upvote_ratio}  {comments} {flair} {subreddit_info} {created_at}"
    )


def render_to_console(
    subreddits: list[Submission], hours_ago: int, base_url: str
) -> None:
    """Renders processed data to console"""

    time_ago = datetime.utcnow() - timedelta(hours=hours_ago)

    console.print(
        f"[bold red]Reddit[/bold red] Showing posts since [bold]{hours_ago}h[/bold] ago 👇"
    )

    for subreddit in subreddits:
        new_posts = subreddit.new()
        filtered_new_posts = [
            p for p in new_posts if datetime.utcfromtimestamp(p.created_utc) > time_ago
        ]

        post_count_text = format_post_count(filtered_new_posts)

        console.print(
            f"\n[black on white] r/{subreddit.display_name} [/black on white] [green]{post_count_text}[/green]"
        )

        if filtered_new_posts:
            for post in sorted(
                filtered_new_posts,
                key=lambda post: post.created_utc,
                reverse=True,
            ):
                console.print(Panel(format_post(post, base_url, _TIMEZONE)))
