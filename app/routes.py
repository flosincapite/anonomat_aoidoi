import re

import flask
import flask_login

import app
from app import blog_post
from app import issue
from app import page
from app import submit_form
from app.login import login_form
from app.login import user


"""
Sidebar:
  - home
  - issues
  - submit
  - blog

ISSUE:
  - embedded multi-page .pdf viewer

SUBMIT:
  - upload & email form

BLOG:
  - displays posts by select writers
"""


class _DummyUser(object):
    def __init__(self, name):
        self._name = name

    def check_password_hash(self, *args, **kwargs):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return self._name


@app.login_manager.user_loader
def load_user(user_id):
    # return app.user_db.get(user_id)
    return _DummyUser(user_id)


@app.wsgi_app.route("/")
@app.wsgi_app.route("/index")
def index():
    return flask.render_template(
        "index2.html", title="Anonomat Aoidoi", page_title="Anonomat Aoidoi"
    )


@app.wsgi_app.route("/blog")
def blog():
    # TODO: Create real posts; make some kind of a database.
    blog_posts = app.blog_db.get_all()
    return flask.render_template("blog.html", blog_posts=blog_posts, page_title="Blog")


@app.wsgi_app.route("/submit")
def submit():
    return flask.render_template(
        "submit.html", page_title="Submit", submit_form=submit_form.SubmitForm()
    )


@app.wsgi_app.route("/submit", methods=["POST"])
def submit_submit():
    return flask.render_template(
        "submit_confirm.html", page_title="Submission Successful"
    )


@app.wsgi_app.route("/issues")
def issues():
    # TODO: Import here: awful hack. Figure out how to generate URLs properly.
    issues = issue.Issue.list()
    return flask.render_template("issues.html", page_title="Issues", issues=issues)


def _file_for(issue, page):
    # TODO: Respect parameters.
    return flask.url_for("static", filename="issues/%s/%s.png" % (issue, page))


@app.wsgi_app.route("/nextpage", methods=["POST"])
def next_page():
    # TODO: This should be part of a separate, private API.
    request = flask.request.get_json()
    print("Request is:")
    print(request)
    dir_str = request.get("direction", "0")
    sign, val = re.search(r"(\+|\-)?(\d*)", dir_str).groups()
    curr_page = int(request.get("currentPage", 0))
    if sign is not None:
        next_page = curr_page + int(dir_str)
    else:
        next_page = int(val)

    the_issue = issue.Issue.from_meta(request["issue"])

    message = None
    if next_page in the_issue.message_pages:
        message = "HELLO"

    response_json = {
        "hasLeft": next_page > int(the_issue.lowest),
        "hasRight": next_page < int(the_issue.highest),
        "nextPage": next_page,
        "message": message,
        "leftPng": _file_for(request["issue"], next_page),
        "rightPng": _file_for(request["issue"], next_page + 1),
    }
    print(response_json)
    response = flask.jsonify(response_json)
    return response, 201


def _file_exists(file_name):
    return True


def _render_section_head(the_issue, page_number, pages, message):
    # TODO: Implement this.
    this_page = pages[page_number]
    return flask.render_template(
        "section_head.html",
        page_title=f"Section Head: {this_page.title}",
        message=message,
        include_contents=this_page.image,
        issue_number=the_issue.number,
        prev_page=pages.get(page_number - 1),
        next_page=pages.get(page_number + 1),
        toc=the_issue.toc,
    )

def _render_author_page(the_issue, page_number, pages, message):
    # TODO: Implement this.
    this_page = pages[page_number]
    return flask.render_template(
        "author_image.html",
        page_title=f"Unimplemented author page for {pages[page_number].author}",
        include_contents=this_page.image,
        message=message,
        issue_number=the_issue.number,
        prev_page=pages.get(page_number - 1),
        next_page=pages.get(page_number + 1),
        toc=the_issue.toc,
    )


def _render_single_poem(the_issue, page_number, pages, message):
    this_page = pages[page_number]
    return flask.render_template(
        "single_poem.html",
        page_title=this_page.title or "Poem",
        page_html=this_page.contents_html,
        message=message,
        issue_number=the_issue.number,
        prev_page=pages.get(page_number - 1),
        next_page=pages.get(page_number + 1),
        toc=the_issue.toc,
    )


def _render_single_image(the_issue, page_number, pages, message):
    this_page = pages[page_number]
    return flask.render_template(
        "single_image.html",
        page_title=this_page.title or "Image",
        include_contents=this_page.image,
        message=message,
        issue_number=the_issue.number,
        prev_page=pages.get(page_number - 1),
        next_page=pages.get(page_number + 1),
        toc=the_issue.toc,
    )


_RENDER_METHODS = {
    "section_head": _render_section_head,
    "author_page": _render_author_page,
    "single_poem": _render_single_poem,
    "single_image": _render_single_image,
}


@app.wsgi_app.route("/viewer/<re('(\d+)'):issue_number>/<re('(\d+)'):page_number>")
def single_page(issue_number, page_number):
    # TODO: Consult page number!
    issue_number, page_number = map(int, (issue_number, page_number))
    the_issue = issue.Issue.create(issue_number)

    if page_number <= 0:
        left_number = None
    else:
        left_number = page_number - 1

    if page_number >= the_issue.highest:
        right_number = None
    else:
        right_number = page_number + 1

    pages = page.Page.list(issue_number, page_number - 1, page_number + 1)
    pages = {the_page.page_number: the_page for the_page in pages}

    # TODO: Get left and right pages, too.
    this_page = pages[page_number]
    app.wsgi_app.logger.error(this_page)

    message = None
    if next_page in the_issue.message_pages:
        message = the_issue.message

    return _RENDER_METHODS[this_page.type](the_issue, page_number, pages, message)


@app.wsgi_app.route("/login", methods=["GET", "POST"])
def login(error=None):
    form = login_form.LoginForm()
    if form.validate_on_submit():

        # Create a new user.
        the_user = None
        if form.create_new.data:
            try:
                the_user = user.User.create(form.name.data, form.password.data)
            except ValueError:
                return flask.redirect("login", error="User already exists")
        if the_user is None:
            the_user = user.User.get(form.name.data)

        # TODO: Remove this.
        the_user = _DummyUser(form.name.data)
        # End TODO
        if form.login.data:
            if the_user.check_password_hash(form.password.data):
                flask_login.login_user(the_user)
                return flask.redirect("index")

    return flask.render_template("login.html", page_title="Login", login_form=form)


@app.wsgi_app.route("/blog_post", methods=["GET"])
def blog_post_template():
    pass


@app.wsgi_app.route("/blog_post", methods=["GET"])
def new_post():
    pass
