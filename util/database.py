import json
import os
import sqlite3


def _create_tables(connection):
    c = connection.cursor()
    c.execute(
        """
      CREATE TABLE issues (
          id INTEGER PRIMARY KEY AUTOINCREMENT, title text, cover_png text,
          table_of_contents text);"""
    )
    c.execute(
        """
      CREATE TABLE pages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          issue_number int, page_number int, author text, title text, type text,
          contents_html text, image text, background_image text,
          FOREIGN KEY(issue_number) REFERENCES issues(id));"""
    )
    connection.commit()


def _populate_database(meta_dict, table_of_contents, connection):
    # TODO: meta_dict and table_of_contents no longer need to be separate.
    cover_png = meta_dict.get("cover")
    title = meta_dict.get("title")
    issue = meta_dict.get("issue")
    new_toc = {'issue': issue}

    c = connection.cursor()

    def _pages():
        page = 0
        while True:
            page += 1
            yield page

    page = _pages()
    for section in table_of_contents.get("sections", []):
        section_list = new_toc.setdefault("subcontents", [])
        section_dict = {}
        section_list.append(section_dict)
        section_dict["title"] = section["title"]
        base_dir = section.get("base_dir", "")
        cover = section.get("cover")
        if cover is not None:
            next_page = next(page)
            section_dict["__page"] = next_page
            cover = os.path.join(base_dir, cover)
            c.execute(
                "INSERT INTO pages (issue_number, page_number, image, title, type) "
                "values (?, ?, ?, ?, ?)",
                (issue, next_page, cover, section["title"], "section_head"),
            )
        for author in section.get("authors", []):
            author_background = author.get("image", "")
            if author_background:
                author_background = os.path.join(base_dir, author_background)
            author_list = section_dict.setdefault("subcontents", []) 
            author_dict = {}
            author_list.append(author_dict)
            author_dict["title"] = author["name"]
            next_page = next(page)
            author_dict["__page"] = next_page
            c.execute(
                "INSERT INTO pages (issue_number, page_number, image, author, type) "
                "values (?, ?, ?, ?, ?)",
                (issue, next_page, author_background, author["name"], "author_page"),
            )

            for poem in author.get("poems", []):
                poem_list = author_dict.setdefault("subcontents", [])
                poem_list.append({})
                poem_dict = poem_list[-1]
                next_page = next(page)
                poem_dict["__page"] = next_page
                if poem.get("contents_html") is not None:
                    poem_dict["title"] = poem.get("title", "Untitled Poem")
                    c.execute(
                        "INSERT INTO pages "
                        "(issue_number, page_number, title, contents_html, author, background_image, type) "
                        "values (?, ?, ?, ?, ?, ?, ?)",
                        (
                            issue,
                            next_page,
                            poem["title"],
                            os.path.join(base_dir, poem["contents_html"]),
                            author["name"],
                            author_background,
                            "single_poem"
                        )
                    )
                else:
                    assert poem.get("image") is not None
                    poem_dict["title"] = poem.get("title", "Untitled Image")
                    c.execute(
                        "INSERT INTO pages "
                        "(issue_number, page_number, title, author, image, type) "
                        "values (?, ?, ?, ?, ?, ?)",
                        (
                            issue,
                            next_page,
                            poem.get("title", ""),
                            author["name"],
                            os.path.join(poem["image"]),
                            "single_image"
                        ),
                    )

            closing_image = author.get("closing_image")
            if closing_image is not None:
                poem_list.append({})
                poem_dict = poem_list[-1]
                next_page = next(page)
                poem_dict["__page"] = next_page
                poem_dict["title"] = "Closing Image"
                c.execute(
                    "INSERT INTO pages (issue_number, page_number, title, image, author, type) "
                    "values (?, ?, ?, ?, ?, ?)",
                    (issue, next_page, "Closing Image", author_background, author["name"], "single_image"),
                )
    
    toc_string = json.dumps(new_toc)
    c.execute(
        "INSERT INTO issues (id, title, cover_png, table_of_contents) "
        "values (?, ?, ?, ?);",
        (issue, title, cover_png, toc_string),
    )

    connection.commit()


class DatabaseFrontend:
    def __init__(self, database_file):
        self._connection = sqlite3.connect(database_file)

    def create_database(self):
        _create_tables(self._connection)

    def populate_database(self, meta_file, toc_file):
        with open(meta_file, "r") as inp:
            meta_dict = yaml.load(inp)
        with open(toc_file, "r") as inp:
            toc_dict = yaml.load(inp, Loader=yaml.Loader)
        _populate_database(meta_dict, toc_dict, self._connection)

    def create_and_populate_database(self, meta_file, toc_file):
        self.create_database()
        self.populate_database(meta_file, toc_file)


if __name__ == "__main__":
    import collections
    import yaml
    import fire

    fire.Fire(DatabaseFrontend)
