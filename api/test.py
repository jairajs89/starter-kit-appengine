from xlib.appenginekit import Handler, route
from model.test import Test


@route('/test/')
class TestHandler(Handler):
    def get(self):
        self.respond('Yea.. {}'.format(len(Test.query().fetch(keys_only=True))))
