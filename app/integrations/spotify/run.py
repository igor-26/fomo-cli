import os
from typing import cast

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from app.parser import get_parsed_args

from .utils import (
    get_current_user_followed_artists,
    get_current_user_followed_artists_songs,
    render_to_console,
)

load_dotenv()
ARGS = get_parsed_args()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_DAYS_AGO = cast(int, os.getenv("SPOTIFY_DAYS_AGO"))

SCOPES = [
    "user-follow-read",
    "user-read-playback-state",
    "user-read-currently-playing",
    "user-follow-read",
    "user-library-read",
    "user-read-playback-position",
    "user-top-read",
    "user-read-recently-played",
]


def render_spotify_results():
    # instantiate client
    spotify_client = Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SCOPES,
        )
    )

    # setup render data
    followed_artists_list = get_current_user_followed_artists(
        client=spotify_client, limit=50, _range=500
    )
    days_ago = int(ARGS.spotify_days_ago or SPOTIFY_DAYS_AGO)
    followed_artists_track_list = get_current_user_followed_artists_songs(
        client=spotify_client,
        followed_artists=followed_artists_list,
        days_ago=days_ago,
    )

    render_to_console(followed_artists_track_list)
