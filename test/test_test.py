from xlib.appenginekit.test import TestCase
from model.test import Test


class DudeTest(TestCase):
    def test_test(self):
        assert 0 == len(Test.query().fetch(keys_only=True))
