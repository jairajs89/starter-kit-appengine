from datetime import datetime, timedelta
from os       import environ
from time     import mktime

from google.appengine.ext import ndb


DEBUG = ('Development' in environ.get('SERVER_SOFTWARE', 'Production'))


def datetime_to_millis(dt):
    return int( mktime(value.utctimetuple()) ) * 1000


def millis_to_datetime(value):
    seconds = int(value/1000.0)
    dt = datetime.utcfromtimestamp(seconds) + timedelta(milliseconds=int(value)-seconds*1000)
    return dt


def future_iterator(futures):
    while futures:
        if len(futures) == 1:
            future = futures[0]
        else:
            future = ndb.Future.wait_any(futures)
        futures.remove(future)
        yield future
