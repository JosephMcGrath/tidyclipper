"""
Command-line arguments to drive the clipping tools.
"""

import argparse
import os

from .parse_config import parse_json


def main():
    """
    Run the tool via a command-line tool that picks up a JSON file.
    """
    parser = argparse.ArgumentParser(description="RSS aggregator / clipping.")
    parser.add_argument(
        "config",
        type=str,
        help="Config path.",
        default=os.path.join(os.getcwd(), "config.json"),
    )

    args = parser.parse_args()

    parse_json(args.config)


if __name__ == "__main__":
    main()
