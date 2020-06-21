# TidyClipper

TidyClipper is a simple RSS aggregation tool inspired by reading old books like Sherlock Holmes & H.P. Lovecraft where characters treat newspaper clippings as a way to collate / sift interesting patterns out of large quantities of public data.

The tool fundamentally downloads RSS feeds with ``requests``, parses them with a combination of ``feedparser`` and ``BeautifulSoup`` and then saves them to an SQL database.
Once in the database, entries can be "clipped" into a standalone HTML file with regex.

```py
import tidyclipper

database = tidyclipper.FeedDatabase(r"C:\path\to\database.db")
clipper = tidyclipper.FeedClipper(database)

clipper.add_feed(r"http://feeds.bbci.co.uk/news/rss.xml")

clipper.make_clipping(
    "hound of the baskervilles", r"(?i)hound of the baskervilles", "Hound.html"
)
```

----

For repeated runs, a config file can be passed in, see ``config_example`` for an example of the expected format:

```py
import tidyclipper

tidyclipper.parse_json("config_example.json")
```
