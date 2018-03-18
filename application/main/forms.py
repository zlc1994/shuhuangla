from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms.fields import TextAreaField, SubmitField, StringField


class SettingForm(FlaskForm):
    about_me = TextAreaField('签名', validators=[Length(0, 140)])
    save = SubmitField('保存')

class SearchForm(FlaskForm):
    q = StringField(validators=[DataRequired()])