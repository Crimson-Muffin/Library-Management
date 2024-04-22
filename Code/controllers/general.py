from flask import  request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from controllers import app, db
from models import Book, Section, BookRequest, IssuedBook, Rating
from controllers.forms import BookRequestForm, RateBook, SearchForm
from controllers.utils import *
from sqlalchemy import or_
@app.route('/')
def home():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin'))

    if current_user.is_authenticated:
        books = Book.query.all()
        return render_template('user_home.html',title='Home',books=books)
    else:
        return render_template('home.html', title='Home')


@app.route("/sections")
@login_required
def sections():
    sections = Section.query.all()
    return render_template('sections_page.html', title='Sections', sections=sections)

@app.route("/section/<int:section_id>")
@login_required
def section(section_id):
    books = db.session.query(Book).filter(Book.section_id == section_id).all()
    return render_template('section.html', title='Section', books=books)


@app.route("/my_books")
@login_required
def my_books():
    
    user_books = db.session.query(IssuedBook, Book)\
        .join(Book, IssuedBook.book_id == Book.book_id).filter(IssuedBook.user_id==current_user.user_id).all()

    book_requests = db.session.query(BookRequest, Book)\
        .join(Book, BookRequest.book_id == Book.book_id).filter(BookRequest.user_id==current_user.user_id).all()
    return render_template('user_books.html', title='My Books', books=user_books, book_requests=book_requests)



@app.route("/book/<int:book_id>")
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('home'))
    
    if has_permission(current_user,book):
        return render_template('book.html', title='Book Detail', book=book)
    else:
        flash('You do not have permission to view this book Request this book', 'danger')
        return redirect(url_for('request_book', book_id=book_id))

        


@app.route('/request_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def request_book(book_id):
    
    book = Book.query.get_or_404(book_id)

    if BookRequest.query.filter_by(book_id=book_id,user_id=current_user.user_id).first():
        flash('Book is already requested', 'danger')
        return redirect(url_for('home'))
    if IssuedBook.query.filter_by(book_id=book_id,user_id=current_user.user_id).first():
        flash('Book is already issued', 'danger')
        return redirect(url_for('home'))
    
    requests =len(BookRequest.query.filter_by(user_id=current_user.user_id).all()) + len(IssuedBook.query.filter_by(user_id=current_user.user_id).all())
    if requests > 5:
        flash('You can not request more than 5 books', 'danger')
        return redirect(url_for('home'))

    form = BookRequestForm()
    if form.validate_on_submit():
        return_date = form.return_date.data
        book_request = BookRequest(user_id=current_user.user_id, book_id=book_id, return_date=return_date)
        db.session.add(book_request)
        db.session.commit()
        flash('Book requested successfully', 'success')
        return redirect(url_for('home'))
    return render_template('request_book.html', title='Request Book', book=book, form=form)


@app.route('/cancel_request/<int:book_id>', methods=['GET', 'POST'])
@login_required
def cancel_request(book_id):
    book_request = BookRequest.query.filter_by(book_id=book_id,user_id=current_user.user_id).first()
    if book_request:
        db.session.delete(book_request)
        db.session.commit()
        flash('Request cancelled successfully', 'success')
        return redirect(url_for('home'))
    else:
        flash('Request not found', 'danger')
        return redirect(url_for('home'))


@app.route('/return_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def return_book(book_id):
    issued_book = IssuedBook.query.filter_by(book_id=book_id,user_id=current_user.user_id).first()
    if issued_book:
        db.session.delete(issued_book)
        db.session.commit()
        flash('Book returned successfully', 'success')
        return redirect(url_for('home'))
    else:
        flash('Book is not issued', 'danger')
        return redirect(url_for('home'))
    


@app.route('/rate_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def rate_book(book_id):
    book = Book.query.get_or_404(book_id)

    rating = Rating.query.filter_by(book_id=book_id,user_id=current_user.user_id).first()
    

    if rating:
        
        flash('You have already rated this book', 'danger')
        return redirect(url_for('home'))
    

    form = RateBook()
    if form.validate_on_submit():
        rating_value = form.rating.data
        feedback = form.feedback.data
        rating = Rating(user_id=current_user.user_id, book_id=book_id, rating=rating_value, feedback=feedback)
        db.session.add(rating)
        db.session.commit()
        flash('Book rated successfully', 'success')
        return redirect(url_for('home'))
    return render_template('rate_book.html', title='Rate Book', book=book, form=form)
    

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_result():
    form = SearchForm()

    if form.validate_on_submit():
        query = form.query.data
        sections = Section.query.filter(Section.name.like('%'+query+'%')).all()
        books = Book.query.filter(
            or_(
                Book.name.like('%'+query+'%'),
                Book.description.like('%'+query+'%'),
                Book.author.like('%'+query+'%')
            )
        ).all()
        print(sections)
        print(books)
        return render_template('search_results.html', title='Search', sections=sections, books=books, query=query)
    return render_template('search_form.html', title='Search', form=form)


