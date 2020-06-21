import datetime
import random
import re
import sqlite3
from typing import List

import feedparser
import requests
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
    @classmethod
    def from_entry(
        cls, entry: feedparser.FeedParserDict, feed: feedparser.FeedParserDict
    ):
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
        return f"## {self.title}\n\n* {self.time}\n* {self.feed}\n* {self.link}\n\n{self.summary}\n\n---"


class FeedDatabase:
    def __init__(self, file: str):
        self.file = file

        self._make_tables()

    def _make_tables(self):
        statements = [
            """
        CREATE TABLE IF NOT EXISTS entry(
            title TEXT
          , feed TEXT
          , link TEXT PRIMARY KEY
          , time TEXT
          , source TEXT
          , summary TEXT
        );
        """,
            "CREATE INDEX IF NOT EXISTS title_idx ON entry(title);",
            "CREATE INDEX IF NOT EXISTS summary_idx ON entry(summary);",
            "CREATE TABLE IF NOT EXISTS feed (url TEXT PRIMARY KEY, last_fetched TEXT NOT NULL);",
        ]
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            for statment in statements:
                cur.execute(statment)

    def write_entries(self, entries: List[FeedEntry]) -> None:
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            for entry in entries:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO entry
                    (title, summary, link, time, feed, source)
                    VALUES (?,?,?,?,?,?);""",
                    (
                        entry.title,
                        entry.summary,
                        entry.link,
                        entry.time,
                        entry.feed,
                        entry.source,
                    ),
                )
            for feed in {x.source for x in entries}:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO feed
                    (url, last_fetched)
                    VALUES (?, ?);""",
                    (feed, datetime.datetime.now().isoformat()),
                )

    def get_feeds(self, mode="standard") -> List[str]:
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            if mode == "standard":
                cur.execute("SELECT url FROM feed ORDER BY last_fetched ASC;")
            elif mode == "shuffle":
                cur.execute("SELECT url FROM feed ORDER BY RANDOM();")
            return [x[0] for x in cur.fetchall()]

    def search(self, regex: str):
        pattern = re.compile(regex)
        output = []
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            for row in cur.execute(
                "SELECT title, summary, link, time, feed, source FROM entry ORDER BY time DESC;"
            ):
                if re.search(pattern, row[0] or "") or re.search(pattern, row[1] or ""):
                    temp = {x[0]: y for x, y in zip(cur.description, row)}
                    output.append(FeedEntry(**temp))
        return output


class FeedClipper:
    def __init__(self, database: FeedDatabase):
        self.session = requests.session()
        self.database = database

    def add_feed(self, url: str) -> None:
        try:
            raw = self.session.get(url, timeout=1)
            feed = feedparser.parse(raw.text)
        except:
            return
        feed["href"] = raw.url
        new_entries = [FeedEntry.from_entry(x, feed) for x in feed.entries]
        self.database.write_entries(new_entries)

    def add_feeds(self, urls: List[str]):
        for url in urls:
            print(url)
            self.add_feed(url)

    def recycle(self, mode="standard"):
        for url in self.database.get_feeds(mode):
            print(url)
            self.add_feed(url)
