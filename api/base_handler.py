import logging
import json

from google.appengine.api import users
from google.appengine.api.datastore_errors import BadValueError
from google.appengine.api.validation import ValidationError
from google.appengine.ext import ndb
import webapp2

from lib.utils import DEBUG, millis_to_datetime
from model.base_model import BaseModel


ORIGINS = '*'
OPTIONS_CACHE = 365 * 24 * 60 * 60  # 1 year


allowed_methods = webapp2.WSGIApplication.allowed_methods
webapp2.WSGIApplication.allowed_methods = allowed_methods.union(('PATCH',))


def is_admin(*args, **kwargs):
    if len(args) > 0 and isinstance(args[0], webapp2.RequestHandler):
        if args[0].request.headers.get('X-AppEngine-Cron'):
            return True
        elif args[0].request.headers.get('X-AppEngine-QueueName'):
            return True
    return DEBUG or users.is_current_user_admin()


def admin_only(func):
    def wrapper(self, *args, **kwargs):
        if not is_admin(self, *args, **kwargs):
            logging.info('user must be admin')
            self.redirect(users.create_login_url('/'))
        else:
            return func(self, *args, **kwargs)
    return wrapper


class BaseHandler(webapp2.RequestHandler):
    Model = None
    _read_only = []

    def initialize(self, *args, **kwargs):
        value = super(BaseHandler, self).initialize(*args, **kwargs)
        try:
            self.body_params = json.loads(self.request.body)
        except:
            self.body_params = {}
        self.params = {}
        self.params.update(self.request.params)
        self.params.update(self.body_params)
        return value

    def _populate_entity(self, entity):
        props = self.Model._include
        if props is None:
            props = self.Model._properties.keys()
        for prop in self.Model._exclude:
            if prop in props:
                props.remove(prop)
        for prop in self._read_only:
            if prop in props:
                props.remove(prop)
        if 'id' in props:
            props.remove('id')
        for prop in props:
            if prop in self.body_params:
                value = self.body_params[prop]
                prop_field = getattr(self.Model, prop)
                if isinstance(prop_field, ndb.ComputedProperty):
                    continue
                elif isinstance(prop_field, ndb.DateTimeProperty):
                    if prop_field._repeated:
                        try:
                            value = [millis_to_datetime(v) for v in value]
                        except:
                            raise BadValueError('failed to parse datetime')
                    else:
                        try:
                            if value:
                                value = millis_to_datetime(value)
                            else:
                                value = None
                        except:
                            raise BadValueError('failed to parse datetime')
                elif isinstance(prop_field, ndb.KeyProperty):
                    if prop_field._repeated:
                        value = [ndb.Key(prop_field._kind, v) for v in value]
                        if None in ndb.get_multi(value):
                            raise BadValueError('stored key must reference an existing entity')
                    else:
                        if value:
                            value = ndb.Key(prop_field._kind, value)
                            if value.get() is None:
                                raise BadValueError('stored key must reference an existing entity')
                        else:
                            value = None
                entity.populate(**{prop: value})

    def handle_exception(self, exception, debug):
        logging.exception(exception)
        if isinstance(exception, BadValueError) or isinstance(exception, ValidationError):
            self.response.set_status(400)
        else:
            self.response.set_status(500)
        self.response.write('An error occurred.')

    def security_headers(self):
        self.response.headers['X-Frame-Options'] = 'DENY'

    def cache_header(self, cache_life=0):
        if cache_life:
            self.response.headers['Cache-Control'] = 'public, max-age=%s' % cache_life
        else:
            self.response.headers['Cache-Control'] = 'no-cache'

    def cors_headers(self):
        self.response.headers['Access-Control-Allow-Origin'] = ORIGINS
        self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        self.response.headers['Access-Control-Max-Age'] = str(OPTIONS_CACHE)

    def options(self, *args, **kwargs):
        self.security_headers()
        self.cors_headers()
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        self.cache_header(OPTIONS_CACHE)

    def respond(self, data,
                content_type='application/json', cache_life=0, headers={}):
        self.security_headers()
        self.cors_headers()
        self.cache_header(cache_life)

        for header, value in headers.items():
            if header == 'Content-Type':
                content_type = value
            else:
                self.response.headers[header] = value

        if content_type == 'application/json':
            if isinstance(data, BaseModel):
                data = data.to_dict()
            elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], BaseModel):
                data = [e.to_dict() for e in data]
            data = json.dumps(data, separators=(',', ':'))

        self.response.headers['Content-Type'] = content_type
        self.response.out.write(data)

    def respond_error(self, code, message='', cache_life=0, headers={}):
        self.response.set_status(code)
        self.security_headers()
        self.cors_headers()
        self.cache_header(cache_life)
        for header, value in headers.items():
            self.response.headers[header] = value
        if 'Content-Type' not in headers:
            self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(message)


class RESTHandler(BaseHandler):
    def get_list(self):
        return [e for e in self.Model.query() if self._can_do('read', e)]

    def can_create(self, entity): return False

    def can_read(self, entity): return False

    def can_update(self, entity, existing_entity): return False

    def can_delete(self, entity): return False

    def _can_do(self, action, *args):
        func = getattr(self, 'can_'+action)
        if isinstance(func, bool):
            return func
        else:
            try:
                return func(*args) or False
            except:
                return False

    def get(self, entity_id):
        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)
        if not entity_id:
            if self.get_list:
                entities = self.get_list()
            else:
                entities = None
            if entities is None:
                self.respond_error(403, 'forbidden')
            else:
                self.respond(entities)
        else:
            entity = self.Model.get_by_id(entity_id)
            if entity is None:
                self.respond_error(404, 'not found')
            else:
                if not self._can_do('read', entity):
                    self.respond_error(403, 'forbidden')
                else:
                    self.respond(entity)

    def post(self, entity_id):
        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)
        if entity_id:
            existing_entity = self.Model.get_by_id(entity_id)
            if existing_entity is None:
                self.respond_error(404, 'not found')
                return
        else:
            existing_entity = None
        if entity_id:
            entity = self.Model(id=entity_id)
        else:
            entity = self.Model()
        self._populate_entity(entity)
        if entity_id:
            if not self._can_do('update', entity, existing_entity):
                self.respond_error(403, 'forbidden')
            else:
                entity.put()
                self.respond(entity)
        else:
            if not self._can_do('create', entity):
                self.respond_error(403, 'forbidden')
            else:
                entity.put()
                self.respond(entity)

    def put(self, entity_id):
        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)
        if not entity_id:
            self.respond_error(405, 'method not allowed')
            return
        existing_entity = self.Model.get_by_id(entity_id)
        entity = self.Model(id=entity_id)
        self._populate_entity(entity)
        if existing_entity:
            if not self._can_do('update', entity, existing_entity):
                self.respond_error(403, 'forbidden')
            else:
                entity.put()
                self.respond(entity)
        else:
            if not self._can_do('create', entity):
                self.respond_error(403, 'forbidden')
            else:
                entity.put()
                self.respond(entity)

    def patch(self, entity_id):
        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)
        if not entity_id:
            self.respond_error(405, 'method not allowed')
            return
        existing_entity = self.Model.get_by_id(entity_id)
        if existing_entity is None:
            self.respond_error(404, 'not found')
            return
        entity = self.Model(key=existing_entity.key)
        for prop, _ in self.Model._properties.iteritems():
            prop_field = getattr(self.Model, prop)
            if not isinstance(prop_field, ndb.ComputedProperty):
                entity.populate(**{prop: getattr(existing_entity, prop)})
        self._populate_entity(entity)
        if not self._can_do('update', entity, existing_entity):
            self.respond_error(403, 'forbidden')
        else:
            entity.put()
            self.respond(entity)

    def delete(self, entity_id):
        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)
        if not entity_id:
            self.respond_error(405, 'method not allowed')
            return
        entity = self.Model.get_by_id(entity_id)
        if entity is None:
            self.respond_error(404, '')
        else:
            if not self._can_do('delete', entity):
                self.respond_error(403, '')
            else:
                entity.key.delete()
                self.respond(entity)
