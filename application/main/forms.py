from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.fields import TextAreaField, SubmitField, StringField


class SettingForm(FlaskForm):
    about_me = TextAreaField('签名', validators=[Length(0, 140)])
    save = SubmitField('保存')

class SearchForm(FlaskForm):
    q = StringField(validators=[DataRequired()])

class SubmitNewBookForm(FlaskForm):
    url = StringField('网址', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_url(self, url):
        domains = ['qidian.com', 'zongheng.com']
        if not any([domain in url.data for domain in domains]):
            raise ValidationError('暂不支持该网站')
