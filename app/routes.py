import flask
import flask_login

import app
from app import blog_post
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


ISSUE_TO_PAGES = {}


class _DummyUser(object):
  def __init__(self,name):
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


@app.wsgi_app.route('/')
@app.wsgi_app.route('/index')
def index():
  return flask.render_template(
      'index.html', title='Anonomat Aoidoi', page_title='Anonomat Aoidoi')


@app.wsgi_app.route('/blog')
def blog():
  # TODO: Create real posts; make some kind of a database.
  blog_posts = app.blog_db.get_all()
  return flask.render_template(
      'blog.html', blog_posts=blog_posts, page_title='Blog')


@app.wsgi_app.route('/submit')
def submit():
  return flask.render_template(
      'submit.html', page_title='Submit', submit_form=submit_form.SubmitForm())


@app.wsgi_app.route('/submit', methods=['POST'])
def submit_submit():
  return flask.render_template(
      'submit_confirm.html', page_title='Submission Successful')


@app.wsgi_app.route('/issues')
def issues():
  # TODO: Import here: awful hack. Figure out how to generate URLs properly.
  from app import issue
  return flask.render_template(
      'issues.html', page_title='Issues', issues=issue.Issue.list())


def _file_for(issue, page):
  # TODO: Respect parameters.
  return flask.url_for('static', filename='issues/%s/%s.pdf' % (issue, page))


@app.wsgi_app.route('/nextpage', methods=['POST'])
def next_page():
  # TODO: This should be part of a separate, private API.
  request = flask.request.get_json()
  next_page = sum(map(
    int,
    [request.get('direction', 0), request.get('currentPage', 0)]))
  response = flask.jsonify({
    'hasLeft': True,
    'hasRight': True,
    'nextPage': next_page,
    'pdfFile': _file_for(int(request.get('issue', 0)), next_page)})
  return response, 201


def _file_exists(file_name):
  return True


@app.wsgi_app.route('/viewer/<re(\'(\d+)\'):issue_number>/<re(\'(\d+)\'):page_number>')
def single_page(issue_number, page_number):
  # TODO: Consult page number!
  this_page = int(page_number)
  prev_page = this_page - 1
  if prev_page <= 0:
    prev_page = -1
  next_page = this_page + 1
  if not _file_exists(this_page):
    next_page = -1
  return flask.render_template(
      'view_pdf.html', page_title='Issue %s' % issue_number,
      pdf_file=_file_for(*map(str, [issue_number, page_number])),
      prev_page=prev_page, next_page=next_page)


@app.wsgi_app.route('/login', methods=['GET', 'POST'])
def login(error=None):
  form = login_form.LoginForm()
  if form.validate_on_submit():

    # Create a new user.
    the_user = None
    if form.create_new.data:
      try:
        the_user = user.User.create(form.name.data, form.password.data)
      except ValueError:
        return flask.redirect('login', error='User already exists')
    if the_user is None:
      the_user = user.User.get(form.name.data)

    # TODO: Remove this.
    the_user = _DummyUser(form.name.data)
    # End TODO
    if form.login.data:
      if the_user.check_password_hash(form.password.data):
        flask_login.login_user(the_user)
        return flask.redirect('index')
  
  return flask.render_template('login.html', login_form=form)
