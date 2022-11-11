from datetime import datetime, timedelta
from textwrap import dedent

from rich.console import Console
from rich.progress import track as rich_track
from spotipy import Spotify


console = Console()


def get_current_user_followed_artists(
    client: Spotify, limit: int, _range: int
) -> list[dict]:
    """Returns a list of dicts with `id` and `name` keys of current user followed artists"""

    current_user_followed_artists = []
    for offset in range(0, _range, limit):
        response = client.current_user_followed_artists(limit=limit, after=offset)

        artists = response["artists"]["items"]

        for _artist in artists:
            name = _artist["name"]
            id = _artist["id"]

            current_user_followed_artists.append(
                {
                    "id": id,
                    "name": name,
                }
            )

    return current_user_followed_artists


def get_date_token(release_date_precision: str, parse: bool) -> str:
    """Returns date token based on the release date precision"""

    if release_date_precision == "day":
        if parse:
            return "%Y-%m-%d"
        return "%b %-d %Y"

    if release_date_precision == "month":
        if parse:
            return "%Y-%m"
        return "%b %Y"

    if release_date_precision == "year":
        return "%Y"

    return ""


def get_current_user_followed_artists_songs(
    client: Spotify, followed_artists: list[dict], days_ago: int
) -> list[dict]:
    """Returns list of track dicts sorted by release date in descending order"""

    all_artists_tracks: list[dict] = []

    for artist in rich_track(
        followed_artists,
        description=f"[bold green]Spotify[/bold green] Finding songs released since [bold]{days_ago}d[/bold] ago",
    ):

        all_artist_tracks = client.search(type="track", q=f"artist:{artist['name']}")[
            "tracks"
        ]["items"]

        formatted_all_artist_tracks = []
        for _track in all_artist_tracks:
            # need to convert release date from stamp
            release_date_str = _track["album"]["release_date"]
            release_date_precision = _track["album"]["release_date_precision"]

            parse_token = get_date_token(
                release_date_precision=release_date_precision, parse=True
            )

            # apply parse token
            release_date = datetime.strptime(release_date_str, parse_token)

            # filter out tracks that have been released after the criteria
            if not release_date > datetime.utcnow() - timedelta(days=days_ago):
                continue

            # there can be several artist on a track
            artists_list = [
                {
                    "name": artist["name"],
                    "url": artist["external_urls"]["spotify"],
                }
                for artist in _track["artists"]
            ]

            # keep track of this because URLs can repeat
            all_tracks_urls = [track["url"] for track in all_artists_tracks]

            # append only if the same URL is not present already
            if _track["external_urls"]["spotify"] not in all_tracks_urls:

                formatted_all_artist_tracks.append(
                    {
                        "name": _track["name"],
                        "url": _track["external_urls"]["spotify"],
                        "artists": artists_list,
                        "release_date": release_date,
                        "release_date_precision": _track["album"][
                            "release_date_precision"
                        ],
                        "duration_ms": _track["duration_ms"],
                    },
                )

        all_artists_tracks += formatted_all_artist_tracks

    return sorted(
        all_artists_tracks,
        key=lambda track: track["release_date"],
        reverse=True,
    )


def format_artists(artists_list: list[dict], delimiter: str) -> str:
    """Returns formatted list of track artists"""

    formatted_artists_list = []
    for _artist in artists_list:
        formatted_artists_list.append(
            f"[green][link={_artist['url']}]{_artist['name']}[/link][/green]"
        )

    return delimiter.join(formatted_artists_list)


def format_track(track: dict) -> str:
    """Returns formatted track representation"""

    title = f"[red bold][link={track['url']}]{track['name']}[/link][/red bold]"
    duration = (
        f" {datetime.fromtimestamp(track['duration_ms'] / 1000).strftime('%M:%S')}"
    )
    artists = f"{format_artists(track['artists'], ', ')}"
    format_token = get_date_token(
        release_date_precision=track["release_date_precision"], parse=False
    )
    release_date = (
        f"[white bold]{track['release_date'].strftime(format_token)}[/white bold]"
    )

    return dedent(f"{title}" f"{duration}" f" by {artists}" f" on {release_date}")


def render_to_console(track_list: list[dict]) -> None:
    """Renders processed data to console"""

    for idx, track in enumerate(track_list):
        console.print(f"{str(idx+1)}. {format_track(track)}")
