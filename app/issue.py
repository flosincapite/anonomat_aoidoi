import collections
import os
import re
import threading

import flask
import yaml

import app


_Issue = collections.namedtuple(
    'Issue', ['title', 'pages', 'number', 'lowest', 'highest', 'cover'])


_CACHE = {}
_CACHE_LOCK = threading.Lock()


def _meta_for(directory):
  return os.path.join(directory, 'meta.yaml')


class Issue(_Issue):
  """Represents a single issue of the journal."""
  
  DATA_DIRECTORY = app.wsgi_app.config['DATABASE_DIRECTORY']

  @classmethod
  def from_meta(cls, number):
    if number not in _CACHE:
      with _CACHE_LOCK:
        issue_directory = os.path.join(cls.DATA_DIRECTORY, number)
        meta_file = _meta_for(issue_directory)
        with open(meta_file, 'r') as inp:
          config = yaml.load(inp)
        
        pages = []
        for file_name in os.listdir(issue_directory):
          match = re.search(r'^(\d+)\.png$', file_name)
          if match:
            pages.append(match.groups()[0])

        pages = list(map(str, sorted(map(int, pages))))

        the_issue = Issue(
            title=config['title'], pages=pages, number=number, lowest=pages[0],
            highest=pages[-1], cover=config['cover'])
        _CACHE[number] = the_issue
    return _CACHE[number]

  @classmethod
  def list(cls):
    issue_numbers = [
        subdir for subdir in os.listdir(cls.DATA_DIRECTORY)
        if os.path.isfile(_meta_for(os.path.join(cls.DATA_DIRECTORY, subdir)))]
    issues = []
    for issue in sorted(issue_numbers):
      issues.append(cls.from_meta(issue))
    return issues
