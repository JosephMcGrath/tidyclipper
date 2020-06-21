"""
Tools to manage individual entries from RSS feeds.
"""

import datetime
import re

import feedparser
from bs4 import BeautifulSoup


def sanitise_html(html: str) -> str:
    """
    Removes a set of tags from a HTML string.

    Intended to return HTML that can be embeded in a larger document.
    """
    soup = BeautifulSoup(html, "lxml")

    for tag in ["img", "script", "embed", "iframe"]:
        for entry in soup.findAll(tag):
            entry.extract()

    output = str(soup)
    output = re.sub(r"^<\/?html>", "", output)
    output = re.sub(r"^<\/?body>", "", output)
    return output


class FeedEntry:
    """
    A single entry from an RSS feed.
    """

    @classmethod
    def from_rss(
        cls, entry: feedparser.FeedParserDict, feed: feedparser.FeedParserDict
    ):
        """
        Converts a feedparser entry / feed into a FeedEntry.
        """
        try:
            time = datetime.datetime(*entry.published_parsed[:6]).isoformat()
        except (AttributeError, TypeError):
            time = datetime.datetime.now().isoformat()
        return cls(
            title=entry.get("title"),
            summary=entry.get("summary"),
            link=entry.get("link"),
            time=time,
            feed=feed.feed.get("title"),
            source=feed.get("href"),
        )

    def __init__(self, title, summary, link, time, feed, source):
        self.title = title.strip()
        self.summary = summary
        self.link = link
        self.time = time
        self.feed = feed
        self.source = source

        try:
            self.summary = sanitise_html(self.summary)
        except TypeError:
            pass

    def __hash__(self):
        return hash(self.link)

    def __repr__(self):
        return f"<Feed Entry : {self.title[:50]}>"

    def as_markdown(self):
        """
        Convert the feed entry to a simple markdown output format.
        """
        output = f"## {self.title}\n\n"
        output += f"* {self.time}\n* {self.feed}\n* {self.link}\n\n"
        output += f"{self.summary}\n\n---"
        return output
