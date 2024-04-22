from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField,DateField,DateTimeField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User,Section,Book
import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        mail = User.query.filter_by(email=email.data).first()
        if mail:
            raise ValidationError(
                'Email is already taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class NewSectionForm(FlaskForm):
    section_name = StringField('Name', validators=[DataRequired(), Length(min=2)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Create Section')

    def validate_section_name(self, section_name):
        section = Section.query.filter_by(name=section_name.data).first()

        if section:
            raise ValidationError(
                "Section name is already taken. Please choose a different one.")
        
class UpdateSectionForm(FlaskForm):
    section_name = StringField('Name', validators=[DataRequired() , Length(min=2)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Update Section')


class NewBookForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2)])
    author = StringField('Author', validators=[DataRequired(), Length(min=2)])
    file_name = FileField('Upload Book', validators=[FileRequired(), FileAllowed(['pdf'])])
    section = RadioField('Select Section', coerce=int,render_kw={'class':'no_bullets'},validators=[DataRequired()])
    submit = SubmitField('Create Book')

    def validate_section(self, section):
        section = Section.query.filter_by(section_id=section.data).first()
        if not section:
            raise ValidationError('Section not found. Please select a valid section.')

class UpdateBookForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2)])
    author = StringField('Author', validators=[DataRequired(), Length(min=2)])
    file_name = FileField('Upload Book', validators=[DataRequired(),FileAllowed(['pdf'])],render_kw={'accept': '.pdf'})
    section = RadioField('Select Section', coerce=int,render_kw={'class':'no_bullets'},validators=[DataRequired()])
    submit = SubmitField('Update Book')


class RateBook(FlaskForm):
    rating = RadioField('Rate Book', choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')], coerce=int,render_kw={'class':'no_bullets'})
    feedback = TextAreaField('Feedback', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Rate Book')


class BookRequestForm(FlaskForm):
    return_date = DateField('Return Date',format='%Y-%m-%d' ,validators=[DataRequired()])
    submit = SubmitField('Request Book')

    def validate_book_id(self, book_id):
        book = Book.query.filter_by(book_id=book_id.data).first()
        if not book:
            raise ValidationError('Book not found. Please enter a valid book id.')
    
    def validate_return_date(self, return_date):
        if return_date.data <= datetime.date.today():
            raise ValidationError('Return date must be a future date.')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()],render_kw={'placeholder':'Search'})
    submit = SubmitField('Search')