"""
Functionality to run the tool from a config file.
"""

import json

from .feed_clipper import FeedClipper
from .feed_database import FeedDatabase


def parse_json(file_path: str) -> None:
    """
    Runs the tool based on a config file.
    """

    with open(file_path, encoding="utf-8") as file:
        config = json.load(file)

    database = FeedDatabase(config["database"])
    clipper = FeedClipper(database)

    if config.get("refetch", False):
        clipper.refetch()

    clipper.add_feeds(config.get("new_feeds", []))

    for clipping in config.get("clippings", []):
        clipper.make_clipping(
            title=clipping["title"], regex=clipping["regex"], file=clipping["file"]
        )
