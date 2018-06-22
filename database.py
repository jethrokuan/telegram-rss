"""Database for Telegram RSS Bot"""

from environs import Env
import pyrebase
from utils import date_to_string, now, string_to_date

env = Env()


class Database(object):
    def __init__(self, firebase_config):
        firebase = pyrebase.initialize_app(firebase_config)
        self._db = firebase.database()
        self._storage = firebase.storage()

    def add_feed(self, user_id, feed_url):
        feeds = self._db.child("users").child(user_id).child("feeds").get()
        feeds = feeds.val() or []
        feeds.append(feed_url)
        self._db.child("users").child(user_id).child("feeds").set(feeds)

    def get_feeds(self, user_id):
        return self._db.child("users").child(user_id).child(
            "feeds").get().val()

    def remove_feed(self, user_id, idx):
        feeds = self._db.child("users").child(user_id).child("feeds").get()
        feeds = feeds.val()
        if feeds and idx < len(feeds) - 1:
            feed = feeds[idx]
            del feeds[idx]
        else:
            raise ValueError(
                "Unable to delete at index...")  # TODO: better error message
        self._db.child("users").child(user_id).child("feeds").set(feeds)
        return feed

    def update_fetch_date(self, user_id):
        datetime_str = date_to_string(now())
        self._db.child("users").child(user_id).child("last_fetch").set(
            datetime_str)

    def get_fetch_date(self, user_id):
        datetime_str = self._db.child("users").child(user_id).child(
            "last_fetch").get().val()
        if datetime_str:
            return string_to_date(datetime_str)
        else:
            return None

    def get_users(self):
        return self._db.child("users").get().val()


with env.prefixed('FIREBASE_'):
    config = {
        "apiKey": env('APIKEY'),
        "authDomain": env('AUTHDOMAIN'),
        "databaseURL": env('DATABASEURL'),
        "storageBucket": env('STORAGEBUCKET')
    }

database = Database(config)
