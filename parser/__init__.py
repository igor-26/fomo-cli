from argparse import ArgumentParser, Namespace


def get_parsed_args() -> Namespace:
    """Returns namespace of global args"""

    parser = ArgumentParser(description="Consume social media content via CLI")

    # reddit
    parser.add_argument(
        "--reddit-hours-ago", type=int, help="Hours since post creation"
    )

    reddit_flags_group = parser.add_mutually_exclusive_group()
    reddit_flags_group.add_argument(
        "--reddit-include", nargs="+", help="List of subreddits to include"
    )
    reddit_flags_group.add_argument(
        "--reddit-exclude", nargs="+", help="List of subreddits to exclude"
    )

    # spotify
    parser.add_argument(
        "--spotify-days-ago", type=int, help="Days since released"
    )

    # twitter
    parser.add_argument(
        "--twitter-hours-ago", type=int, help="Hours since tweet creation"
    )
    twitter_flags_group = parser.add_mutually_exclusive_group()

    twitter_flags_group.add_argument(
        "--twitter-include", nargs="+", help="List of users to include"
    )
    twitter_flags_group.add_argument(
        "--twitter-exclude", nargs="+", help="List of users to exclude"
    )
    parser.add_argument(
        "--twitter-retweets", action="store_true", help="Include retweets"
    )
    parser.add_argument(
        "--twitter-replies", action="store_true", help="Include replies"
    )

    # general
    CHOICES = ["reddit", "spotify", "twitter"]
    general_flags_group = parser.add_mutually_exclusive_group()
    general_flags_group.add_argument(
        "--integrations-include",
        nargs="+",
        choices=CHOICES,
        help="List of integrations to include",
    )
    general_flags_group.add_argument(
        "--integrations-exclude",
        nargs="+",
        choices=CHOICES,
        help="List of integrations to exclude",
    )

    return parser.parse_args()
