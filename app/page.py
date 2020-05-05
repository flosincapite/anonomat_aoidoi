import cachetools

import app


class Page(object):

  _CACHE = cachetools.TTLCache(maxsize=30, ttl=3600)
  _DATABASE = app.db
  
  def __init__(
      self, issue, page_number, author, image=None, title=None,
      contents_html=None, page_type=None, topbar=None):
    self._author = author
    self._issue = issue
    self._page_number = page_number
    self._image = image
    self._contents_html = contents_html
    self._type = page_type

  @property
  def author(self):
    return self._author

  @property
  def issue(self):
    return self._issue

  @property
  def page_number(self):
    return self._page_number

  @property
  def image(self):
    return self._image

  @property
  def contents_html(self):
    return self._contents_html

  @property
  def type(self):
    return self._type

  def __str__(self):
    return f'Page with author {self._author} issue {self._issue} page_number {self._page_number} image {self._image} contents_html {self._contents_html}'

  @classmethod
  def list(cls, issue_number, lowest_page, highest_page):
    c = cls._DATABASE.cursor()
    print(c.execute('PRAGMA table_info(pages)').fetchall())
    c.execute(
        'SELECT page_number, author, image, title, contents_html, type '
        'FROM pages WHERE page_number >= ? AND page_number <= ?', 
        (lowest_page, highest_page))
    return [Page(*((issue_number,) + row)) for row in c.fetchall()]
