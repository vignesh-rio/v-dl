from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

class DownloadForm(FlaskForm):
    url = StringField('Video URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Download')
