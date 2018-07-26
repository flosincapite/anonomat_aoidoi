import os


class Config(object):
  SECRET_KEY = os.environ.get('ANONOMAT_KEY') or 'anonomat_aoidoi'
  DATABASE_DIRECTORY = '/home/cory/projects/online_journal/app/static/issues'
