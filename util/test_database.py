import json
import sqlite3
import unittest 

from util import database


class DatabaseTest(unittest.TestCase):

  def setUp(self):
    # Database will be stored in temporary file.
    self._connection = sqlite3.Connection("")
    database.create_tables(self._connection)

  def tearDown(self):
    self._connection.close()

  def test_populate_database(self):
    meta_dict = {
      'issue': 1,
      'title': 'Issue 1',
      'cover': 'some/file.png',
    }

    table_of_contents = {
      'sections': [
        {
          'title': 'Section 1',
          'authors': [
            {
              'name': 'Sappho',
              'plate_png': 'static/media/grecian_urn.png',
              'poems': [
                {
                  'title': 'Hoi men hippeon',
                  'contents_html': 'static/poems/hoi_men_hippeon.html',
                },
                {
                  'title': 'Deduke men ha selanna',
                  'contents_html': 'static/poems/deduke_men_ha_selanna.html',
                },
              ],
            },
            {
              'name': 'Keats',
              'plate_png': 'static/media/tb.png',
              'poems': [
                {
                  'title': 'Pot of Basil',
                  'contents_html': 'static/poems/pot_of_basil.html',
                },
              ],
            },
          ],
        },
        {
          'title': 'Section 2',
          'authors': [
            {
              'name': 'Marsyas',
              'plate_png': 'static/media/regular_urn.png',
              'poems': [
                {
                  'title': 'Bad Jokes',
                  'contents_html': 'static/poems/bad_jokes.html',
                },
              ],
            },
          ],
        },
      ],
    }

    database.populate_database(meta_dict, table_of_contents, self._connection)

    c = self._connection.cursor()
    c.execute('SELECT * FROM issues ORDER BY id')
    issues = c.fetchall()
    self.assertEqual(1, len(issues))
    issue_id, issue_title, cover_png, toc_string = issues[0]
    self.assertEqual(1, issue_id)
    self.assertEqual('Issue 1', issue_title)
    self.assertEqual('some/file.png', cover_png)
    self.assertEqual(table_of_contents, json.loads(toc_string))

    c.execute('SELECT * FROM authors ORDER BY id')
    authors = c.fetchall()
    self.assertEqual(
        [
            (1, 1, 'static/media/grecian_urn.png', 'Sappho'),
            (2, 1, 'static/media/tb.png', 'Keats'),
            (3, 1, 'static/media/regular_urn.png', 'Marsyas'),
        ], authors)

    c.execute('SELECT * FROM poems ORDER BY id')
    poems = c.fetchall()
    self.assertEqual(
        [
            (1, 1, 'Hoi men hippeon', 'static/poems/hoi_men_hippeon.html'),
            (
                2, 1, 'Deduke men ha selanna',
                'static/poems/deduke_men_ha_selanna.html'),
            (3, 2, 'Pot of Basil', 'static/poems/pot_of_basil.html'),
            (4, 3, 'Bad Jokes', 'static/poems/bad_jokes.html'),
        ], poems)


if __name__ == '__main__':
  unittest.main()
