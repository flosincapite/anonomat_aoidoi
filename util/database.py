import os
import random
import yaml


class YamlDatabase(object):

  def __init__(
      self, directory, data_type, initializer=None, key_func=None,
      serialize=None):
    self._directory = directory
    if initializer is None:
      initializer = lambda yaml_dict: data_type(**yaml_dict)
    self._initializer = initializer
    self._key_func = key_func
    if serialize is None:
      serialize = lambda entity: entity._asdict()
    self._serialize = serialize

  @property
  def key_func(self):
    return self._key_func

  @key_func.setter
  def key_func(self, key_func):
    self._key_func = key_func

  def _entities_from_file(self, file_name):
    with open(os.path.join(self._directory, file_name), 'r') as inp:
      things = yaml.load(inp)
      return [self._initializer(e) for e in things]
      # return map(self._initializer, yaml.load(inp))

  def get_all(self):
    result = []
    for file_name in os.listdir(self._directory):
      result.extend(
          self._entities_from_file(os.path.join(self._directory, file_name)))
    return result

  def get(self, key):
    # TODO: Create a proper database!!!
    if self._key_func is None:
      raise ValueError('Database needs a key_func to index by keys.')
    for entity in self.get_all():
      if self.key_func(entity) == key:
        return entity
    return None
        
  def put(self, entity):
    # TODO: This is stupid.
    if self._serialize is None:
      raise ValueError('Database needs a serialize function to put entries.')
    file_name = os.path.join(
        self._directory, random.choice(os.listdir(self._directory)))
    elements = list(self._entities_from_file(file_name))
    elements.append(entity)

    with open(file_name, 'w') as outp:
      yaml.dump(list(map(self._serialize, elements)), outp)
