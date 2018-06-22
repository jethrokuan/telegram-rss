import feedparser
import datetime


def get_articles(feed_url, entries=4):
    feeds = feedparser.parse(feed_url)
    return [{
        "title": entry["title"],
        "link": entry["link"],
        "date_published": get_entry_date(entry)
    } for entry in feeds.get("entries")[:entries]]


def get_entry_date(entry):
    published_parsed = entry.get("published_parsed")
    created_parsed = entry.get("created_parsed")
    updated_parsed = entry.get("updated_parsed")

    if published_parsed:
        return datetime.datetime(*published_parsed[:6])
    elif created_parsed:
        return datetime.datetime(*created_parsed[:6])
    elif updated_parsed:
        return datetime.datetime(*updated_parsed[:6])
    else:
        return None
