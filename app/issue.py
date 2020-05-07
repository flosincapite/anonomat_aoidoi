import cachetools
import collections
import json
import os
import re
import threading

import flask
import yaml

import app
from app import table_of_contents


_Issue = collections.namedtuple(
    'Issue', [
      'title', 'number', 'lowest', 'highest', 'cover', 'toc', 'message_pages',
      'message'])


def _meta_for(directory):
  return os.path.join(directory, 'meta.yaml')


def _toc_for(directory):
  return os.path.join(directory, 'toc.yaml')


class Issue(_Issue):
  """Represents a single issue of the journal."""
  
  _DATABASE = app.db
  _CACHE = cachetools.TTLCache(maxsize=10, ttl=3600)
  _CACHE_LOCK = threading.Lock()

  @classmethod
  def create(cls, number):
    number = str(number)
    if number not in cls._CACHE:
      with cls._CACHE_LOCK:

        c = cls._DATABASE.cursor()
        c.execute(
            'SELECT title, cover_png, table_of_contents '
            'FROM issues WHERE id=?', number)
        rows = c.fetchall()
        if len(rows) != 1:
          # Implies this issue wasn't in database.
          app.wsgi_app.logger.error(
              f'Tried to fetch issue {number}, which is not in the database.')
          return None

        title, cover_png, toc_json = rows[0]
        toc = table_of_contents.generate(toc_json)

        c.execute(
            'SELECT MIN(page_number) FROM pages WHERE issue_number=?', number)
        lowest, = c.fetchall()[0]
        c.execute(
            'SELECT MAX(page_number) FROM pages WHERE issue_number=?', number)
        highest, = c.fetchall()[0]

        # TODO: Re-enable this functionality.
        if 'topbars' in toc:
          first, last = map(int, config['topbars']['range'].split('-'))
          message_pages = set(range(first, last + 1))
          message = config['topbars']['message']
        else:
          message_pages = set([])
          message = None

        the_issue = Issue(
            title=title, number=number, lowest=lowest, highest=highest,
            cover=cover_png, toc=toc, message_pages=message_pages,
            message=message)

        cls._CACHE[number] = the_issue

    return cls._CACHE[number]

  @classmethod
  def list(cls):
    c = cls._DATABASE.cursor()
    c.execute('SELECT id FROM issues')
    issue_numbers = [number for number, in c.fetchall()]
    issues = []
    for issue in sorted(issue_numbers):
      issues.append(cls.create(issue))
    return issues
