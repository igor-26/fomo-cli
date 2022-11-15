from argparse import Namespace
from typing import Callable


def get_integration_render_functions(
    function_map: dict[str, Callable], parsed_args: Namespace
) -> list[Callable]:
    """Returns list of integration render functions for the enabled integrations"""

    include_args = parsed_args.integrations_include
    exclude_args = parsed_args.integrations_exclude

    if include_args:
        return [function_map[arg] for arg in include_args]

    if exclude_args:
        return [function_map[k] for k in function_map.keys() if k not in exclude_args]

    return list(function_map.values())


def build_integration_function_map(
    enabled_integrations: list[str],
) -> dict[str, Callable]:
    """Returns map of integration render functions"""

    integration_function_map = {}

    if "reddit" in enabled_integrations:
        from app.integrations.reddit import init as render_reddit_results

        integration_function_map["reddit"] = render_reddit_results

    if "twitter" in enabled_integrations:
        from app.integrations.twitter import init as render_twitter_results

        integration_function_map["twitter"] = render_twitter_results

    if "spotify" in enabled_integrations:
        from app.integrations.spotify import init as render_spotify_results

        integration_function_map["spotify"] = render_spotify_results

    return integration_function_map
