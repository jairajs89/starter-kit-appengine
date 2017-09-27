from datetime import datetime

from google.appengine.ext import ndb

from lib.utils import datetime_to_millis, millis_to_datetime


class BaseModel(ndb.Model):
    _include    = None
    _exclude    = []
    _fetch_keys = True

    def to_dict(self, include=None, exclude=None, fetch_keys=None):
        if include is None:
            if self._include is not None:
                include = self._include
        if exclude is None:
            exclude = []
        if fetch_keys is None:
            fetch_keys = self._fetch_keys
        exclude.extend(self._exclude)
        props = {}
        if 'id' not in exclude and (include is None or 'id' in include) and self.key:
            props['id'] = self.key.id()
        for key, prop in self._properties.iteritems():
            if key not in exclude and (include is None or key in include):
                if hasattr(self, key):
                    value = getattr(self, key)
                    if isinstance(value, datetime):
                        value = datetime_to_millis(value)
                    elif isinstance(value, ndb.Key):
                        if fetch_keys:
                            value = value.get().to_dict()
                        else:
                            value = value.id()
                    elif isinstance(value, (list, tuple)) and len(value) > 0:
                        if isinstance(value[0], datetime):
                            value = [datetime_to_millis(v) for v in value]
                        elif isinstance(value[0], ndb.Key):
                            if fetch_keys:
                                value = [e.to_dict() for e in ndb.get_multi(value)]
                            else:
                                value = [k.id() for k in value]
                    props[key] = value
        return props
