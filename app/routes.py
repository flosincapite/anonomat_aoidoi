import flask

import app
from app import blog_post
from app import submit_form


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


@app.wsgi_app.route('/')
@app.wsgi_app.route('/index')
def index():
  return flask.render_template(
      'index.html', title='Anonomat Aoidoi', page_title='Anonomat Aoidoi')


@app.wsgi_app.route('/blog')
def blog():
  blog_posts = [
      blog_post.BlogPost(
        author='Juvenalis', date='then', title='Custodes?',
        cdata='quis custodiet ipsos/'),
      blog_post.BlogPost(
        author='Valmiki', date='then', title='Birds',
        cdata='kuujantam raama raameti'),
  ] 
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
  result = flask.url_for('static', filename='issues/%d/%d.pdf' % (issue, page))
  return flask.url_for('static', filename='issues/issue_1.pdf')


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
    'pdfFile': _file_for(int(request.get('issue', 1)), next_page)})
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
      pdf_file=flask.url_for(
        'static',
        filename='issues/issue_%s.pdf' % issue_number),
      prev_page=prev_page, next_page=next_page)
