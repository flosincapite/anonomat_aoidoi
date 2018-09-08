import collections

import app

import werkzeug.security


_User = collections.namedtuple('_User', ['name', 'password'])


class User(_User):

  def __init__(self, *args, **kwargs):
    super().__init__()
    self.password = werkzeug.security.generate_password_hash(self.password)

  @classmethod
  def create(cls, name, password):
    existing = cls.get(name)
    if existing is not None:
      raise ValueError('User with name "%s" already exists.' % name)
    new_user = cls(name=name, password=password)
    app.user_db.put(new_user)
    return new_user

  @classmethod
  def get(cls, name):
    return app.user_db.get(name)

  def validate(self, password):
    return werkzeug.security.check_password_hash(self._password_hash, password)
