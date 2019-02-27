import collections
import flask


_BlogPost = collections.namedtuple(
    'BlogPost', ['author', 'cdata', 'date', 'title'])


class BlogPost(_BlogPost):
  """Represents a single post on the blog's stream."""

  @property
  def markup(self):
    return flask.Markup(self.cdata)
