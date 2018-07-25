import collections


_BlogPost = collections.namedtuple(
    'BlogPost', ['author', 'cdata', 'date', 'title'])


class BlogPost(_BlogPost):
  """Represents a single post on the blog's stream."""
  pass
