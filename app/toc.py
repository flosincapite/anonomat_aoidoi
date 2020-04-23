import collections
import yaml

import flask


_Toc = collections.namedtuple('TOC', ['markup', 'ids'])


def get_toc(config_file):
  try:
    with open(config_file, 'r') as inp:
      config = yaml.load(inp, Loader=yaml.Loader)
  except FileNotFoundError:
    return None
    
  lines = []
  ids = []

  def _traverse_toc(d):
    lines.append('<ul style="list-style-type:none;">')

    for key, val in d.items():
      if isinstance(val, int):
        new_id = 'toc-item-%d' % len(ids)
        ids.append(new_id)
        lines.append(
          '<li><span class="toc-item" id="%s" data-page="%d">%s</span></li>' % (
            new_id, val, key))
      else:
        lines.append('<li>%s</li>' % key)
        _traverse_toc(val)

    lines.append('</ul>')

  _traverse_toc(config)

  return _Toc(markup=flask.Markup('\n'.join(lines)), ids=ids)
