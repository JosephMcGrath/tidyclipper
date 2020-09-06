"""
Tools to store feed entries in an SQLite database.
"""
import datetime
import logging
import random
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
              , successful_fetches INTEGER DEFAULT(1)
              , failed_fetches INTEGER DEFAULT(0)
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
        logger.debug("Writing %s entries to the database.", len(entries))
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
                    INSERT OR IGNORE INTO feed
                    (url, last_fetched) VALUES (?, ?);
                    """,
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
                    "SELECT url, successful_fetches, failed_fetches FROM feed ORDER BY last_fetched ASC;"
                )
            elif sorting == "shuffle":
                cur.execute(
                    "SELECT url, successful_fetches, failed_fetches FROM feed ORDER BY RANDOM();"
                )
        return [
            x[0]
            for x in cur.fetchall()
            if x[1] >= x[2] or random.random() > x[1] / x[2]
        ]

    def update_feed(self, feed_url: str, success: bool) -> None:
        """
        Set a feed to inactive.
        """
        logger = logging.getLogger(self.log_name)
        logger.debug("Updating feed: %s (success = %s).", feed_url, success)
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE feed SET last_fetched = ? WHERE url = ?;",
                (datetime.datetime.now().isoformat(), feed_url),
            )
            if success:
                cur.execute(
                    "UPDATE feed SET successful_fetches = successful_fetches + 1 WHERE url = ?;",
                    (feed_url,),
                )
            else:
                cur.execute(
                    "UPDATE feed SET failed_fetches = failed_fetches + 1 WHERE url = ?;",
                    (feed_url,),
                )

    def search(self, regex: List[str]) -> List[FeedEntry]:
        """
        Searches the database for any entries that match the provided regex.
        """
        logger = logging.getLogger(self.log_name)
        logger.debug("Searching database for entries matching %s.", regex)
        patterns = [re.compile(x) for x in regex]
        output: List[FeedEntry] = []
        with sqlite3.connect(self.file) as conn:
            cur = conn.cursor()
            for row in cur.execute(
                "SELECT title, summary, link, time, feed, source FROM entry ORDER BY time DESC;"
            ):
                if any(
                    [
                        re.search(x, row[0] or "") or re.search(x, row[1] or "")
                        for x in patterns
                    ]
                ):
                    temp = {x[0]: y for x, y in zip(cur.description, row)}
                    output.append(FeedEntry(**temp))
        logger.debug("Found %s entries.", len(output))
        return output
