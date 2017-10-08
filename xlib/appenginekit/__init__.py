from sys import path
from os import listdir
path.append('./')

try:
    import webapp2
except:
	from .test import TestCase
	TestCase # Linter.. I beat you ;)

import webapp2
from google.appengine.ext import ndb

from .utils import DEBUG
from .handler import Handler
from .model import Model


class WarmupHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello, world!')


routes = [
    (r'/_ah/warmup', WarmupHandler),
]
for file_name in listdir('api'):
    if not file_name.startswith('.') and file_name.endswith('.py') and file_name != '__init__.py':
        api_name = file_name[:-3]
        api_module = __import__('api.%s' % api_name).__getattribute__(api_name)
        if hasattr(api_module, 'routes'):
            routes += api_module.routes

app = ndb.toplevel(webapp2.WSGIApplication(routes, debug=DEBUG))
