import collections
import os
import re
import threading

import flask
import yaml

import app
from app import toc


_Issue = collections.namedtuple(
    'Issue', ['title', 'pages', 'number', 'lowest', 'highest', 'cover', 'toc'])


_CACHE = {}
_CACHE_LOCK = threading.Lock()


def _meta_for(directory):
  return os.path.join(directory, 'meta.yaml')


def _toc_for(directory):
  return os.path.join(directory, 'toc.yaml')


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
        
        toc_file = _toc_for(issue_directory)
        toc_obj = toc.get_toc(toc_file)
        
        pages = []
        for file_name in os.listdir(issue_directory):
          match = re.search(r'^(\d+)\.png$', file_name)
          if match:
            pages.append(match.groups()[0])

        pages = list(map(str, sorted(map(int, pages))))

        the_issue = Issue(
            title=config['title'], pages=pages, number=number, lowest=pages[0],
            highest=pages[-1], cover=config['cover'], toc=toc_obj)
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
