import os
from argparse import Namespace
from datetime import datetime, timedelta
from typing import Iterator, Tuple, cast

import pytz
from dotenv import load_dotenv
from praw.models.reddit.submission import Submission
from praw.models.reddit.subreddit import Subreddit
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding

from app.lib import create_link

load_dotenv()
console = Console()
_TIMEZONE = cast(str, os.getenv("_TIMEZONE"))
REDDIT_BASE_URL = "https://www.reddit.com"


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


def get_post_type(
    post: Submission,
) -> Tuple[str, str]:
    """Returns tuple of post type and emoji representation based on available post properties"""

    if hasattr(post, "post_hint"):
        post_hint = post.post_hint

        if post_hint == "image":
            return "image", f"🖼 "

        if post_hint in ["hosted:video", "rich:video"]:
            return "video", "🎥"

    if hasattr(post, "is_gallery"):
        return "gallery", "🌌"

    return "link", "🔗"


def render_post(
    post: Submission,
    base_url: str,
    _timezone: str,
) -> None:
    """Renders individual post to console"""

    ## data setup
    post_type, post_hint_emoji = get_post_type(post)

    exclusive_thumbnail_tags = ["nsfw", "spoiler"]
    allowed_thumbnail_post_types = [
        "image",
        "video",
        "gallery",
    ]

    should_render_thumbnail = (
        post_type in allowed_thumbnail_post_types
        and post.thumbnail not in exclusive_thumbnail_tags
    )

    subreddit_link = create_link(
        href=f"{base_url}/{post.subreddit_name_prefixed}",
        label=post.subreddit_name_prefixed,
        style="green",
    )
    author_link = create_link(
        href=f"{base_url}/user/{post.author}",
        label=f"u/{post.author}",
        style="green",
    )
    header = f"[bold white]{post_hint_emoji} {post_type.capitalize()}[/bold white]"
    title_link = create_link(
        href=base_url + post.permalink,
        label=post.title,
        style="green",
    )
    ups = f"[red]↑{post.ups}[/red]"
    upvote_ratio = format_ratio(post.upvote_ratio)
    comments = f"💬 {post.num_comments}"
    flair = f"[white]{f' | [bold white]{post.link_flair_text}[/bold white]' if post.link_flair_text else ''}"
    subreddit_info = f"| {author_link} in {subreddit_link}"
    created_at = f"| [b]{datetime.fromtimestamp(post.created_utc, pytz.timezone(_timezone)).strftime('%b %-d %H:%M')}[/b] ({_timezone})"
    selftext = post.selftext if len(post.selftext) else ""

    ## render line by line
    padding_values = (0, 2, 0, 2)

    # top border
    console.rule(
        style="white",
        title=header,
    )

    # title
    console.print(Padding(title_link, padding_values))

    # body
    if selftext:
        console.print("", Padding(Markdown(selftext), padding_values), "")

    # thumbnail
    if should_render_thumbnail:
        console.print()
        console.print(" " * 2, end="")
        os.system(f"imgcat {post.thumbnail}")
        console.print("", end="")

    # View source
    if hasattr(post, "url_overridden_by_dest"):
        post_tag = (
            f" [white on red] {post.thumbnail} [/white on red]"
            if post.thumbnail in exclusive_thumbnail_tags
            else ""
        )
        view_source_link = create_link(
            href=post.url_overridden_by_dest,
            label=f"View source{post_tag}",
            style="bold blue",
        )
        console.print(
            Padding(
                view_source_link,
                padding_values,
            ),
            "",  # nl
        )

    # post info
    console.print(
        Padding(
            f"{ups}  {upvote_ratio}  {comments} {flair} {subreddit_info} {created_at}",
            padding_values,
        )
    )

    # bottom border
    console.rule(style="white")


def render_to_console(
    subreddits: list[Subreddit],
    hours_ago: int,
) -> None:
    """Renders processed data to console"""

    time_ago = datetime.utcnow() - timedelta(hours=hours_ago)

    console.print(
        f"[bold red]Reddit[/bold red] Showing posts since [bold]{hours_ago}h[/bold] ago 👇",
        end="",
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
                render_post(
                    post=post,
                    base_url=REDDIT_BASE_URL,
                    _timezone=_TIMEZONE,
                )
