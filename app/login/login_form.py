import flask_wtf
import wtforms
import wtforms.validators


class LoginForm(flask_wtf.FlaskForm):
  name = wtforms.StringField(
      'Name', validators=[wtforms.validators.DataRequired()])
  password = wtforms.StringField(
      'Password', validators=[wtforms.validators.DataRequired()])
  create_new = wtforms.SubmitField('Create')
  login = wtforms.SubmitField('Login')

  def secrettt(self):
    return self.hidden_tag()
