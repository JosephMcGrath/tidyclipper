"""
Downloads, cleans up and stores entries from RSS feeds.
"""

from typing import List

import feedparser
import requests

from .feed_database import FeedDatabase
from .feed_entry import FeedEntry
from .templates import CLIPPING


class FeedClipper:
    """
    Downloads and saves entries from RSS feeds.
    """

    def __init__(self, database: FeedDatabase):
        self.session = requests.session()
        self.database = database

    def add_feed(self, url: str) -> None:
        """
        Adds a new feed to the database and then clips it.
        """
        try:
            raw = self.session.get(url, timeout=1)
            feed = feedparser.parse(raw.text)
        except:
            return
        feed["href"] = raw.url
        new_entries = [FeedEntry.from_rss(x, feed) for x in feed.entries]
        self.database.write_entries(new_entries)

    def add_feeds(self, urls: List[str]) -> None:
        """
        Clips all entries in a list of feed URLs.
        """
        for url in urls:
            print(url)
            self.add_feed(url)

    def refetch(self, sorting: str = "standard") -> None:
        """
        Fetch all feeds that are already in the database.
        """
        for url in self.database.get_feeds(sorting):
            print(url)
            self.add_feed(url)

    def make_clipping(self, title: str, regex: str, file: str) -> None:
        """
        Make a HTML clipping from from entries matching the provided regex.
        """
        entries = self.database.search(regex)
        with open(file, "w", encoding="utf-8") as output:
            output.write(CLIPPING.render(entries=entries, title=title, pattern=regex))