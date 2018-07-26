"""Converter to allow flask app routes to be written with regex."""


import re

import werkzeug.routing


class RegexConverter(werkzeug.routing.BaseConverter):

  def __init__(self, url_map, *items):
    super().__init__(url_map)
    self._pattern = re.compile(r'^' + items[0] + r'$')

  def to_python(self, value):
    match = self._pattern.search(value)
    if match:
      return match.group()
    return None
