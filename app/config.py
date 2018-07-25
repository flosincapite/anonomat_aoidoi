import os


class Config(object):
  SECRET_KEY = os.environ.get('ANONOMAT_KEY') or 'anonomat_aoidoi'
