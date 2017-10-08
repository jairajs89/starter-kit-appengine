from xlib.appenginekit import Model


class Config(Model):
    # Add environment configuration here as ndb properties

    @property
    @classmethod
    def i(Cls):
        return Cls.get_by_id('config') or Cls(id='config')
