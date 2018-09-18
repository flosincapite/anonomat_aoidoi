import os


class Config(object):
  SECRET_KEY = os.environ.get('ANONOMAT_KEY') or 'anonomat_aoidoi'
  DATABASE_DIRECTORY = '/home/cory/projects/online_journal/app/static/issues'
  BLOG_DIRECTORY = '/home/cory/projects/online_journal/app/static/blog_posts'
  USER_DIRECTORY = '/home/cory/projects/online_journal/data/users'
