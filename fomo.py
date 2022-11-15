import json
import os
from argparse import Namespace
from app.parser import get_parsed_args

from dotenv import load_dotenv

from app.lib import build_integration_function_map, get_integration_render_functions

load_dotenv()

ENABLED_INTEGRATIONS: list[str] = json.loads(os.getenv("ENABLED_INTEGRATIONS"))
ARGS: Namespace = get_parsed_args()


if __name__ == "__main__":
    integration_function_map = build_integration_function_map(
        enabled_integrations=ENABLED_INTEGRATIONS
    )
    integration_functions_to_run = get_integration_render_functions(
        function_map=integration_function_map, parsed_args=ARGS
    )

    for fn in integration_functions_to_run:
        fn()
