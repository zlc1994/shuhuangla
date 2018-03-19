from flask_wtf import FlaskForm
from wtforms.fields import IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    user_id = IntegerField(validators=[DataRequired()])
    book_id = IntegerField(validators=[DataRequired()])
    score = SelectField(
        '评分',
        choices=[(5, 5), (4, 4), (3, 3), (2, 2), (1, 1)],
        coerce=int
    )
    body = TextAreaField('说点什么吧', validators=[DataRequired(message="说点什么吧")])
    submit = SubmitField('提交')
