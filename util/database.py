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
          plate_png text, author int, title text, contents_html text,
          FOREIGN KEY(author) REFERENCES authors(id));''')
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
  cover_png = meta_dict.get('cover')
  title = meta_dict.get('title')
  issue = meta_dict.get('issue')
  toc_string = json.dumps(table_of_contents)
  
  c = connection.cursor()
  print(f'INSERTING issue {issue}.')
  c.execute(
      'INSERT INTO issues (id, title, cover_png, table_of_contents) '
      'values (?, ?, ?, ?);',
      (issue, title, cover_png, toc_string))

  for section in table_of_contents.get('sections', []):
    for author in section.get('authors', []):
      c.execute(
          'INSERT INTO authors (issue_number, plate_png, name) '
          'values (?, ?, ?)',
          (issue, author['plate_png'], author['name']))

      author_id = c.lastrowid
      for poem in author.get('poems', []):
        c.execute(
            'INSERT INTO poems (author, title, contents_html) '
            'values (?, ?, ?)',
            (author_id, poem['title'], poem['contents_html']))
  connection.commit()


class DatabaseFrontend(object):

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
