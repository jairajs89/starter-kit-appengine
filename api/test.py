from xlib.appenginekit import Handler
from model.test import Test


class TestHandler(Handler):
    def get(self):
        self.respond('Yea.. {}'.format(len(Test.query().fetch(keys_only=True))))


routes = [
    ('/test/', TestHandler),
]
