from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_login import current_user
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                     TextAreaField, FileField)
from wtforms.validators import (ValidationError, DataRequired, Email, EqualTo,
                                Length)
from app.models import User

allowed_extensions = ['txt', 'jpg', 'png', 'gif', 'pdf', 'epub', 'mp3', 'mp4', 'm4a']

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={'readonly': True})
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class NewPostForm(FlaskForm):
    # username = current_user.username
    postbody = TextAreaField('New Post', validators=[Length(min=1, max=280)])
    attachment = FileField('Attachment',
                           validators=[FileAllowed(
                               allowed_extensions, 'File type not allowed.')])
    attach_types = allowed_extensions
    submit = SubmitField('Submit')
