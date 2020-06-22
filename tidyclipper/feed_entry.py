"""
Tools to manage individual entries from RSS feeds.
"""

import datetime
import re
import urllib

import feedparser
from bs4 import BeautifulSoup

from .templates import ENTRY


def sanitise_html(html: str) -> str:
    """
    Removes a set of tags from a HTML string.

    Intended to return HTML that can be embeded in a larger document.
    """
    if html is None:
        return ""

    # Wipe out unwwanted tags entirely
    html = re.sub(r"<\/?html>", "", html)
    html = re.sub(r"<\/?body>", "", html)
    html = re.sub(r"<\/?div>", "", html)
    html = re.sub(r"<\/?span>", "", html)

    html = re.sub(r"(\s)+", r"\1", html)

    soup = BeautifulSoup(html, "lxml")

    # Don't want these tags:
    for tag in ["img", "script", "embed", "iframe", "hr"]:
        for entry in soup.findAll(tag):
            entry.extract()

    # Don't want most attributes
    for tag in soup.recursiveChildGenerator():
        if hasattr(tag, "attrs"):
            tag.attrs = {
                key: value for key, value in tag.attrs.items() if key == "href"
            }

    output = soup.prettify()
    output = re.sub(r"<(\/?)h1>", r"<\1h3>", output)
    output = re.sub(r"<(\/?)h2>", r"<\1h3>", output)
    return output


def sanitise_url(url: str) -> str:
    """
    Cleans up a url by removing the query parameter.
    """
    temp = list(urllib.parse.urlparse(url))
    temp[4] = ""
    return urllib.parse.urlunparse(temp)


class FeedEntry:
    """
    A single entry from an RSS feed.
    """

    @classmethod
    def from_rss(
        cls, entry: feedparser.FeedParserDict, feed: feedparser.FeedParserDict
    ) -> "FeedEntry":
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
            link=sanitise_url(entry.get("link")),
            time=time,
            feed=feed.feed.get("title"),
            source=feed.get("href"),
        )

    def __init__(
        self, title: str, summary: str, link: str, time: str, feed: str, source: str
    ):
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

    def __hash__(self) -> int:
        return hash(self.link)

    def __repr__(self) -> str:
        return f"<Feed Entry : {self.title[:50]}>"

    def as_markdown(self) -> str:
        """
        Convert the feed entry to a simple markdown output format.
        """
        output = f"## {self.title}\n\n"
        output += f"* {self.time}\n* {self.feed}\n* {self.link}\n\n"
        output += f"{self.summary}\n\n---"
        return output

    def as_html(self) -> str:
        """
        Formats the feed entry to a snippet of HTML.
        """
        self.summary = sanitise_html(self.summary)
        return ENTRY.render(entry=self)
