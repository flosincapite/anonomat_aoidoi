import collections
import os
import re

import flask
import yaml

import app


_Issue = collections.namedtuple('Issue', ['title', 'pages', 'number'])


class Issue(_Issue):
  """Represents a single issue of the journal."""
  
  DATA_DIRECTORY = app.wsgi_app.config['DATABASE_DIRECTORY']

  @classmethod
  def from_meta(cls, number):
    issue_directory = os.path.join(cls.DATA_DIRECTORY, str(number))
    meta_file = os.path.join(issue_directory, 'meta.yaml')
    with open(meta_file, 'r') as inp:
      config = yaml.load(inp)
    
    pages = []
    for file_name in os.listdir(issue_directory):
      match = re.search(r'^(\d+)\.pdf$', file_name)
      if match:
        pages.append(match.groups()[0])

    return Issue(title=config['title'], pages=pages, number=number)

  @classmethod
  def list(cls):
    def _can_int(string):
      try:
        _ = int(string)
      except:
        return False
      else:
        return True
    issue_numbers = [
        subdir for subdir in os.listdir(cls.DATA_DIRECTORY) if _can_int(subdir)]
    issues = []
    for issue in sorted(map(int, issue_numbers)):
      issues.append(cls.from_meta(issue))
    return issues
