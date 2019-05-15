from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Email, EqualTo, Length
from app.models import User, Movie

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
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class CreateMovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    genre = SelectField('Genre(s)', choices=[('Please Select', 'Please Select'), ('Action', 'action'), ('Comedy', 'comedy'), ('Drama', 'drama'), ('Horror', 'horror'), ('Adventure', 'adventure')])
    submit = SubmitField('Submit')

    def validate_title(self, title):
        movie = Movie.query.filter_by(title=title.data).first()
        if movie is not None:
            raise ValidationError('This movie already exists')

    def validate_genre(self, genre):
        if genre.data == 'Please Select':
            raise ValidationError('Please select a genre')

class DeleteMovieForm(FlaskForm):
    title = SelectField('Select a movie to delete', choices=[('Please Select', 'Please Select')])
    submit = SubmitField('Submit')

    def validate_title(self, title):
        if title.data == 'Please Select':
            raise ValidationError('Please select a movie')

class VoteForm(FlaskForm):
    vote1 = SelectField('Movie Vote #1', choices=[('Please Select', 'Please Select')])
    vote2 = SelectField('Movie Vote #2', choices=[('Please Select', 'Please Select')])
    vote3 = SelectField('Movie Vote #3', choices=[('Please Select', 'Please Select')])
    vote4 = SelectField('Movie Vote #4', choices=[('Please Select', 'Please Select')])
    vote5 = SelectField('Movie Vote #5', choices=[('Please Select', 'Please Select')])
    submit = SubmitField('Submit')

    def validate_vote1(self, vote1):
        if vote1.data == 'Please Select':
            raise ValidationError('Please select a movie')

    def validate_vote2(self, vote2):
        if vote2.data == 'Please Select':
            raise ValidationError('Please select a movie')

    def validate_vote3(self, vote3):
        if vote3.data == 'Please Select':
            raise ValidationError('Please select a movie')

    def validate_vote4(self, vote4):
        if vote4.data == 'Please Select':
            raise ValidationError('Please select a movie')

    def validate_vote5(self, vote5):
        if vote5.data == 'Please Select':
            raise ValidationError('Please select a movie')

class SuggestForm(FlaskForm):
    post = StringField('Suggest a movie to add', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_post(self, post):
        movie = Movie.query.filter_by(title=post.data).first()
        if movie is not None:
            raise ValidationError('This movie already exists')
