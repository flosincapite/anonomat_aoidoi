import json
import sqlite3


def create_tables(connection):
  c = connection.cursor()
  c.execute('''
      CREATE TABLE issues (
          id INTEGER PRIMARY KEY AUTOINCREMENT, title text, cover_png text,
          table_of_contents text);''')
  c.execute('''
      CREATE TABLE pages (
          id INTEGER PRIMARY KEY AUTOINCREMENT, issue_number int,
          page_number int, author text, plate_jpg text, title text, contents_html text,
          FOREIGN KEY(issue_number) REFERENCES issues(id));''')
  c.execute('''
      CREATE TABLE authors (
          id INTEGER PRIMARY KEY AUTOINCREMENT, issue_number int,
          name text,
          FOREIGN KEY(issue_number) REFERENCES issues(id));''')
  c.execute('''
      CREATE TABLE poems (
          id INTEGER PRIMARY KEY AUTOINCREMENT, author int, title text,
          contents_html text, FOREIGN KEY(author) REFERENCES authors(id));''')
  connection.commit()


def populate_database(meta_dict, table_of_contents, connection):
  # TODO: meta_dict and table_of_contents no longer need to be separate.
  cover_png = meta_dict.get('cover')
  title = meta_dict.get('title')
  issue = meta_dict.get('issue')
  toc_string = json.dumps(table_of_contents)
  
  c = connection.cursor()
  c.execute(
      'INSERT INTO issues (id, title, cover_png, table_of_contents) '
      'values (?, ?, ?, ?);',
      (issue, title, cover_png, toc_string))

  def _pages():
    page = 0
    while True:
      page += 1
      yield page

  page = _pages()
  for section in table_of_contents.get('sections', []):
    for author in section.get('authors', []):
      c.execute(
          'INSERT INTO pages (issue_number, page_number, plate_jpg, author) '
          'values (?, ?, ?, ?)',
          (issue, next(page), author['plate_jpg'], author['name']))

      for poem in author.get('poems', []):
        c.execute(
            'INSERT INTO pages '
            '(issue_number, page_number, title, contents_html, author) '
            'values (?, ?, ?, ?, ?)',
            (
                issue, next(page), poem['title'], poem['contents_html'],
                author['name']))
  connection.commit()


class DatabaseFrontend:

  def __init__(self, database_file):
    self._connection = sqlite3.connect(database_file)

  def create_database(self):
    create_tables(self._connection)

  def populate_database(self, meta_file, toc_file):
    with open(meta_file, 'r') as inp:
      meta_dict = yaml.load(inp)
    with open(toc_file, 'r') as inp:
      toc_dict = yaml.load(inp, Loader=yaml.Loader)
    populate_database(meta_dict, toc_dict, self._connection)


if __name__ == '__main__':
  import collections
  import yaml
  import fire

  fire.Fire(DatabaseFrontend)
