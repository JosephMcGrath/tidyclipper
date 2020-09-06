"""
Downloads, cleans up and stores entries from RSS feeds.
"""

import logging
from typing import List

import feedparser
import requests

from .feed_database import FeedDatabase
from .feed_entry import FeedEntry
from .logs import LOG_NAME
from .templates import CLIPPING

REQUEST_ERROR = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ConnectionError,
)


class FeedClipper:
    """
    Downloads and saves entries from RSS feeds.
    """

    def __init__(self, database: FeedDatabase):
        self.log_name = LOG_NAME + ".FeedClipper"
        self.session = requests.session()
        self.database = database

    def add_feed(self, url: str) -> None:
        """
        Adds a new feed to the database and then clips it.
        """
        logger = logging.getLogger(self.log_name)
        logger.info("Fetching feed: %s", url)
        try:
            raw = self.session.get(url, timeout=1)
            feed = feedparser.parse(raw.text)
            feed["href"] = raw.url
            new_entries = [FeedEntry.from_rss(x, feed) for x in feed.entries]
            self.database.update_feed(url, success=True)
        except REQUEST_ERROR:
            logger.debug("Failed to fetch.")
            self.database.update_feed(url, success=False)
            return
        logger.debug("Finished fetching feed (%s entries).", len(new_entries))
        self.database.write_entries(new_entries)

    def add_feeds(self, urls: List[str]) -> None:
        """
        Clips all entries in a list of feed URLs.
        """
        for url in urls:
            self.add_feed(url)

    def refetch(self, sorting: str = "standard") -> None:
        """
        Fetch all feeds that are already in the database.
        """
        logger = logging.getLogger(self.log_name)
        logger.info("Re-fetching all available feeds.")
        for url in self.database.get_feeds(sorting):
            self.add_feed(url)

    def make_clipping(self, title: str, regex: List[str], file: str) -> None:
        """
        Make a HTML clipping from from entries matching the provided regex.
        """
        entries = self.database.search(regex)
        with open(file, "w", encoding="utf-8") as output:
            output.write(CLIPPING.render(entries=entries, title=title, pattern=regex))
