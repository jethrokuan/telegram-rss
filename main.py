#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Description will go here."""

from environs import Env
from database import database
from rss import get_articles
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from utils import is_index
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

env = Env()

_FETCH_INTERVAL = env.int('FETCH_INTERVAL', 300)
logging.info(
    "Bot will fetch feeds at {} second intervals".format(_FETCH_INTERVAL))
_TELEGRAM_TOKEN = env('TELEGRAM_TOKEN', None)

if _TELEGRAM_TOKEN is None:
    raise KeyError("Token not passed.")


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def add_feed(bot, update, args):
    """Add a given feed when the command /add is issued.

    Args:
        args[0]: Feed URL."""
    feed = args[0]
    messages = {
        "help":
        "Sorry! I could not add the entry! "
        "The command format is as follows :\n\n /add <url>"
        "\n\n Here is a short example: \n\n "
        "/add http://www.feedforall.com/sample.xml",
        "invalid_url":
        "'{}' is not a valid feed.",
        "success":
        "'{}' successfully added!"
    }

    if (len(args) != 1):
        update.message.reply_text(messages["help"])
        return

    if not get_articles(feed):
        update.message.reply_text(messages["invalid_url"].format(feed))
        return

    chat_id = update.message.chat_id
    database.add_feed(chat_id, feed)
    update.message.reply_text(messages["success"].format(feed))


def list_feeds(bot, update):
    chat_id = update.message.chat_id
    feeds = database.get_feeds(chat_id)

    update.message.reply_text("\n".join(
        ["{}. {}".format(idx + 1, feed) for idx, feed in enumerate(feeds)]))


def remove_feed(bot, update, args=True):
    """Removes a feed from the feed list by index.

    Args:
        args[0]: index to remove"""
    messages = {
        "help":
        "Usage: /remove <idx> \n\n"
        "<idx> is the index displayed by '/list'",
        "failure":
        "Unable to remove feed at index {}. Are you sure"
        " you got the index right?",
        "success":
        "{} successfully removed!"
    }
    chat_id = update.message.chat_id

    if len(args) != 1 or not is_index(args[0]):
        update.message.reply_text(messages["help"])
        return

    feed_to_remove = int(args[0]) - 1

    try:
        feed = database.remove_feed(chat_id, feed_to_remove)
        update.message.reply_text(messages["success"].format(feed))
    except ValueError:
        messages["failure"].format(feed_to_remove)


def fetch(bot, chat_id):
    logging.info("Fetching feeds for {}".format(chat_id))
    feeds = database.get_feeds(chat_id)

    last_fetch_date = database.get_fetch_date(chat_id)

    for feed in feeds:
        articles = get_articles(feed, entries=10)
        for article in articles:
            date_published = article.get("date_published")
            if not last_fetch_date:
                bot.send_message(
                    chat_id=chat_id,
                    text=u"{} - {}".format(article["title"], article["link"]))
                continue
            if date_published and last_fetch_date < date_published:
                bot.send_message(
                    chat_id=chat_id,
                    text=u"{} - {}".format(article["title"], article["link"]))
    database.update_fetch_date(chat_id)


def manual_fetch_feeds(bot, update):
    chat_id = update.message.chat_id
    return fetch(bot, chat_id)


def fetch_feeds(bot, job):
    user_ids = database.get_users()

    for user_id in user_ids:
        fetch(bot, user_id)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == '__main__':
    logging.info("Connecting to Telegram...")
    updater = Updater(_TELEGRAM_TOKEN)
    logging.info("Connected.")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Job Queue
    job_queue = updater.job_queue

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_feed, pass_args=True))
    dispatcher.add_handler(
        CommandHandler("remove", remove_feed, pass_args=True))
    dispatcher.add_handler(CommandHandler("fetch", manual_fetch_feeds))
    dispatcher.add_handler(CommandHandler("list", list_feeds))
    dispatcher.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # fetch feeds
    job_queue.run_repeating(fetch_feeds, interval=_FETCH_INTERVAL, first=0)

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
