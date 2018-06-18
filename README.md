# Telegram RSS
An intelligent RSS reader for Telegram that learns your preferences,
and summarizes articles for you.

# Why?
Telegram provides an excellent interface for sharing articles with
others, as well as an amazing "instant view" interface on supported
websites. This makes Telegram an excellent platform for reading
feeds.

On the other hand, many feeds contain only a select number of articles
that interest the reader. Hence, from user feedback we can learn
preferences and filter out articles that we are unlikely to read,
allowing us to add a large number of feeds while preserving sanity.

Finally, a short summary of the article can be posted along with the
article link to better inform the reader on whether the article is
worth reading.

# Getting Started

We use [Docker](https://www.docker.com/) for deployment.

```bash
docker build -t telegram-rss .
docker run telegram-rss
```

# Features
- [ ] Manage RSS Feeds
- [ ] Learn user preferences
- [ ] Summarize articles

# Non-features
None comes to mind yet.
