import cachetools

import app


class Page(object):

  _CACHE = cachetools.TTLCache(maxsize=30, ttl=3600)
  _DATABASE = app.db
  
  def __init__(
      self, issue, page_number, author=None, title=None, page_type=None,
      contents_html=None, image=None, background_image=None, topbar=None):
    self._issue = issue
    self._page_number = page_number
    self._author = author
    self._title = title
    self._type = page_type
    self._contents_html = contents_html
    self._image = image
    self._background_image = background_image

  @property
  def issue(self):
    return self._issue

  @property
  def page_number(self):
    return self._page_number

  @property
  def author(self):
    return self._author

  @property
  def title(self):
    return self._title

  @property
  def type(self):
    return self._type

  @property
  def contents_html(self):
    return self._contents_html

  @property
  def image(self):
    return self._image

  @property
  def background_image(self):
    return self._background_image

  def __str__(self):
    return f'Page with author {self._author} issue {self._issue} page_number {self._page_number} image {self._image} contents_html {self._contents_html}'

  @classmethod
  def list(cls, issue_number, lowest_page, highest_page):
    c = cls._DATABASE.cursor()
    result = []
    for page in range(lowest_page, highest_page + 1):
        if page not in cls._CACHE:
            c.execute(
                'SELECT page_number, author, title, type, contents_html, image, background_image '
                'FROM pages WHERE page_number = ? AND issue_number = ?',
                (page, issue_number))
            rows = c.fetchall()
            if not rows:
                continue
            cls._CACHE[page] = Page(*((issue_number,) + rows[0]))
        result.append(cls._CACHE[page])
    return result
