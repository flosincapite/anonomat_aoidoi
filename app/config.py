import os


_ROOT = os.path.dirname(os.path.abspath(__file__))


def _rooted(location):
  return os.path.join(_ROOT, location)


class Config(object):
  SECRET_KEY = os.environ.get('ANONOMAT_KEY') or 'anonomat_aoidoi'
  DATABASE_DIRECTORY = _rooted('static/issues')
  BLOG_DIRECTORY = _rooted('static/blog_posts')
  USER_DIRECTORY = _rooted('data/users')
