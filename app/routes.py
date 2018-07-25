import flask

import app
from app import blog_post
from app import submit


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


@app.wsgi_app.route('/')
@app.wsgi_app.route('/index')
def index():
  return flask.render_template(
      'index.html', title='Anonomat Aoidoi', page_title='Anonomat Aoidoi')


@app.wsgi_app.route('/pdf')
def pdf():
  return flask.render_template(
      'view_pdf.html', pdf_file='static/test.pdf', page_title='Issue 1')


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
      'submit.html', page_title='Submit', submit_form=submit.SubmitForm())
