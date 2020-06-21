"""
Tools to store feed entries in an SQLite database.
"""

import datetime
import logging
import re
import sqlite3
from typing import List

from .feed_entry import FeedEntry
from .logs import LOG_NAME


class FeedDatabase:
    """
    Manages a database containing feed entries.
    """

    def __init__(self, file: str):
        self.log_name = LOG_NAME + ".FeedDatabase"
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
            """
            CREATE TABLE IF NOT EXISTS feed (
                url TEXT PRIMARY KEY
              , last_fetched TEXT NOT NULL
              , to_fetch INTEGER DEFAULT(1)
            );
            """,
        ]
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            for statment in statements:
                cur.execute(statment)

    def write_entries(self, entries: List[FeedEntry]) -> None:
        """
        Write a list of entries to the database.
        """
        logger = logging.getLogger(self.log_name)
        logger.debug("Writing %s logs to disc.", len(entries))
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
                logger.debug("Updaing fetched status of %s.", feed)
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
        logger = logging.getLogger(self.log_name)
        logger.debug("Getting list of available feeds.")
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            if sorting == "standard":
                cur.execute(
                    "SELECT url FROM feed WHERE to_fetch = 1 ORDER BY last_fetched ASC;"
                )
            elif sorting == "shuffle":
                cur.execute(
                    "SELECT url FROM feed WHERE to_fetch = 1 ORDER BY RANDOM();"
                )
            return [x[0] for x in cur.fetchall()]

    def deactivate_feed(self, feed_url) -> None:
        """
        Set a feed to inactive.
        """
        logger = logging.getLogger(self.log_name)
        logger.debug("Deactivating feed: %s.", feed_url)
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE feed SET to_fetch = 0 WHERE url = ?;", (feed_url,))

    def search(self, regex: str) -> List[FeedEntry]:
        """
        Searches the database for any entries that match the provided regex.
        """
        logger = logging.getLogger(self.log_name)
        logger.debug("Searching database for entries matching %s.", regex)
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
        logger.debug("Found %s entries.", len(output))
        return output
