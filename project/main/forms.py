from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

class VideoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    video_file = FileField('Video File', validators=[DataRequired(), FileAllowed(['mp4', 'mov', 'avi'])])
    submit = SubmitField('Upload')
