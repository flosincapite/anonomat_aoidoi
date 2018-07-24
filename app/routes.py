import app
import flask


@app.wsgi_app.route('/')
@app.wsgi_app.route('/index')
def index():
  return flask.render_template('index.html')


@app.wsgi_app.route('/pdf')
def pdf():
  return flask.render_template('view_pdf.html', pdf_file='static/test.pdf')
