import collections
import os
import re
import threading

import flask
import yaml

import app
from app import toc


_Issue = collections.namedtuple(
    'Issue', [
      'title', 'pages', 'number', 'lowest', 'highest', 'cover', 'toc',
      'message_pages', 'message'])


_CACHE = {}
_CACHE_LOCK = threading.Lock()


def _meta_for(directory):
  return os.path.join(directory, 'meta.yaml')


def _toc_for(directory):
  return os.path.join(directory, 'toc.yaml')


class Issue(_Issue):
  """Represents a single issue of the journal."""
  
  _DATABASE = app.db
  _ISSUE_DIRECTORY = app.wsgi_app.config['ISSUE_DIRECTORY']

  @classmethod
  def from_meta(cls, number):
    number = str(number)
    if number not in _CACHE:
      with _CACHE_LOCK:
        issue_directory = os.path.join(cls._ISSUE_DIRECTORY, number)

        meta_file = _meta_for(issue_directory)
        with open(meta_file, 'r') as inp:
          config = yaml.load(inp)
        
        toc_file = _toc_for(issue_directory)
        toc_obj = toc.get_toc(toc_file)
        
        pages = []
        for file_name in os.listdir(issue_directory):
          match = re.search(r'^(\d+)\.png$', file_name)
          if match:
            pages.append(match.groups()[0])

        pages = list(map(str, sorted(map(int, pages))))

        if 'topbars' in config:
          first, last = map(int, config['topbars']['range'].split('-'))
          message_pages = set(range(first, last + 1))
          message = config['topbars']['message']
        else:
          message_pages = set([])
          message = None

        the_issue = Issue(
            title=config['title'], pages=pages, number=number, lowest=pages[0],
            highest=pages[-1], cover=config['cover'], toc=toc_obj,
            message_pages=message_pages, message=message)

        _CACHE[number] = the_issue

    return _CACHE[number]

  @classmethod
  def list(cls):
    c = cls._DATABASE.cursor()
    c.execute('SELECT id FROM issues')
    issue_numbers = [number for number, in c.fetchall()]
    issues = []
    for issue in sorted(issue_numbers):
      issues.append(cls.from_meta(issue))
    return issues
