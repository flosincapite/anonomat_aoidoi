import collections

import flask_wtf


class SubmitForm(flask_wtf.FlaskForm):
  email = wtforms.StringField('Email', validators=[DataRequired()])
  title = wtforms.StringField('Title', validators=[DataRequired()])
  contents = wtforms.StringField('Contents', validators=[DataRequired()])
