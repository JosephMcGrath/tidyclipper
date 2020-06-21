"""
Tools to store feed entries in an SQLite database.
"""

import datetime
import re
import sqlite3
from typing import List

from .feed_entry import FeedEntry


class FeedDatabase:
    """
    Manages a database containing feed entries.
    """

    def __init__(self, file: str):
        self.file = file

        self._make_tables()

    def _make_tables(self) -> None:
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
        """
        Write a list of entries to the database.
        """
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

    def get_feeds(self, sorting: str = "standard") -> List[str]:
        """
        Get a list of feeds from the database. Entries are sorted by the longest time
        since they've been searched (or random if "shuffle" is specified).
        """
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            if sorting == "standard":
                cur.execute("SELECT url FROM feed ORDER BY last_fetched ASC;")
            elif sorting == "shuffle":
                cur.execute("SELECT url FROM feed ORDER BY RANDOM();")
            return [x[0] for x in cur.fetchall()]

    def search(self, regex: str) -> List[FeedEntry]:
        """
        Searches the database for any entries that match the provided regex.
        """
        pattern = re.compile(regex)
        output: List[FeedEntry] = []
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            for row in cur.execute(
                "SELECT title, summary, link, time, feed, source FROM entry ORDER BY time DESC;"
            ):
                if re.search(pattern, row[0] or "") or re.search(pattern, row[1] or ""):
                    temp = {x[0]: y for x, y in zip(cur.description, row)}
                    output.append(FeedEntry(**temp))
        return output
