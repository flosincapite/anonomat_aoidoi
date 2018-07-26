import collections

import flask_wtf
import wtforms
import wtforms.validators


class SubmitForm(flask_wtf.FlaskForm):
  email = wtforms.StringField(
      'Email', validators=[wtforms.validators.DataRequired()])
  title = wtforms.StringField(
      'Title', validators=[wtforms.validators.DataRequired()])
  contents = wtforms.StringField(
      'Contents', validators=[wtforms.validators.DataRequired()])
  submit = wtforms.SubmitField('Submit')

  def secrettt(self):
    return self.hidden_tag()
