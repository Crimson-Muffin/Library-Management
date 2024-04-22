from flask import render_template, flash, redirect, url_for, request
from controllers import app, db
from controllers.forms import NewSectionForm, UpdateSectionForm, NewBookForm, UpdateBookForm, SearchForm
from models import *
from controllers.utils import admin_required
from controllers.utils import save_pdf_file, delete_pdf_file
from sqlalchemy import func, or_
from matplotlib import pyplot as plt

@app.route('/admin')
@admin_required
def admin():
    books = Book.query.all()
    sections = Section.query.all()
    requests = BookRequest.query.all()

    return render_template('admin.html', title='Admin', requests=requests, books=books, sections=sections)


@app.before_request
def before_request():
    revoke_issued_books()

def revoke_issued_books():
    issued_books = IssuedBook.query.all()
    for issued_book in issued_books:
        if issued_book.return_date < datetime.now():
            db.session.delete(issued_book)
            db.session.commit()
            flash('Issued book revoked successfully', 'success')

@app.route('/sections/new', methods=['GET', 'POST'])
@admin_required
def new_section():
    form = NewSectionForm()
    if form.validate_on_submit():
        section = Section(name=form.section_name.data,description=form.description.data)
        db.session.add(section)
        db.session.commit()
        flash('Section created successfully', 'success')

        return redirect(url_for('admin'))
    
    return render_template('new_section.html', form=form, title="New Section")

@app.route('/sections/<int:section_id>/delete', methods=['GET', 'POST'])
@admin_required
def delete_section(section_id):

    section = Section.query.get(section_id)
    books = Book.query.filter_by(section_id=section_id).all()
    
    if not section:
        flash('Section not found', 'danger')
        return redirect(url_for('admin'))
    else:
        for book in books:
            rating = Rating.query.filter_by(book_id=book.book_id).all()
            issued_books = IssuedBook.query.filter_by(book_id=book.book_id).all()
            book_requests = BookRequest.query.filter_by(book_id=book.book_id).all()
            for rate in rating:
                db.session.delete(rate)
            for issued_book in issued_books:
                db.session.delete(issued_book)
            for book_request in book_requests:
                db.session.delete(book_request)
            delete_pdf_file(book.file_name)
            db.session.delete(book)
        db.session.delete(section)
        db.session.commit()
        flash('Section deleted successfully', 'success')
        return redirect(url_for('admin'))
    


@app.route('/sections/<int:section_id>/update', methods=['GET', 'POST'])
@admin_required
def update_section(section_id):
    section = Section.query.get(section_id)
    if section:
        form = UpdateSectionForm()
        if form.validate_on_submit():
            section.name = form.section_name.data
            section.description = form.description.data
            db.session.commit()
            flash('Section updated successfully', 'success')
            return redirect(url_for('admin'))
        
        elif request.method == 'GET':
            form.section_name.data = section.name
            form.description.data = section.description

        return render_template('update_section.html',section=section ,form=form, title="Update Section")
    else:
        flash('Section not found', 'danger')
        return redirect(url_for('admin'))
    

    

@app.route('/sections/<int:section_id>/books', methods=['GET', 'POST'])
@admin_required
def section_books(section_id):
    section = Section.query.get(section_id)
    if not section:
        flash('Section not found', 'danger')
        return redirect(url_for('admin'))

    books_with_ratings_and_feedback = db.session.query(
        Book,
        func.avg(Rating.rating).label('avg_rating'),
        func.group_concat(Rating.feedback).label('feedback_list')
    ).filter(Book.section_id == section_id) \
     .outerjoin(Rating, Book.book_id == Rating.book_id) \
     .group_by(Book.book_id) \
     .all()

    books = [{
        'book': book,
        'avg_rating': avg_rating,
        'feedback_list': (feedback_list or '').split(',')
    } for book, avg_rating, feedback_list in books_with_ratings_and_feedback]

    return render_template('admin_section_books.html', books=books, section=section, title="Section Books")



@app.route('/book/new', methods=['GET', 'POST'])
@admin_required
def new_book():
    form = NewBookForm()
    section = Section.query.all()
    if len(section) == 0:
        flash('Please create a section first', 'danger')
        return redirect(url_for('admin'))

    form.section.choices = [(section.section_id, section.name) for section in Section.query.all()]


    if form.validate_on_submit():
        section_id = form.section.data
        file_name = save_pdf_file(form.file_name.data)

        book = Book(name=form.name.data, description=form.description.data, author=form.author.data, file_name=file_name, section_id=section_id)

        db.session.add(book)
        db.session.commit()
        flash('Book created successfully', 'success')
        return redirect(url_for('admin'))

    return render_template('new_book.html', form=form, title="New Book",section=Section.query.all())


@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        rating = Rating.query.filter_by(book_id=book_id).all()
        issued_books = IssuedBook.query.filter_by(book_id=book_id).all()
        book_requests = BookRequest.query.filter_by(book_id=book_id).all()
        for rate in rating:
            db.session.delete(rate)
        for issued_book in issued_books:
            db.session.delete(issued_book)
        for book_request in book_requests:
            db.session.delete(book_request)
        delete_pdf_file(book.file_name)
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully', 'success')
        return redirect(url_for('admin'))
    else:
        flash('Book not found', 'danger')
        return redirect(url_for('admin'))


    
@app.route('/book/<int:book_id>/update', methods=['GET', 'POST'])
@admin_required
def update_book(book_id):
    book = Book.query.get(book_id)
    if book:
        form = UpdateBookForm(obj=book)
        form.section.choices = [(section.section_id, section.name) for section in Section.query.all()]

        if form.validate_on_submit():
            book.name = form.name.data
            book.description = form.description.data
            book.author = form.author.data
            book.section_id = form.section.data

            if form.file_name.data is not None:
                
                if book.file_name:
                    delete_pdf_file(book.file_name)

                file_name = save_pdf_file(form.file_name.data)
                book.file_name = file_name

            db.session.commit()
            flash('Book updated successfully', 'success')
            return redirect(url_for('admin'))

        elif request.method == 'GET':
            form.name.data = book.name
            form.description.data = book.description
            form.author.data = book.author
            form.section.data = book.section_id

        return render_template('update_book.html', book=book, form=form, title="Update Book", sections=Section.query.all())

    else:
        flash('Book not found', 'danger')
        return redirect(url_for('admin'))


@app.route("/admin/books")
@admin_required
def admin_books():
    books_with_ratings_and_feedback = db.session.query(Book,func.avg(Rating.rating).label('avg_rating'),
        func.group_concat(Rating.feedback).label('feedback_list')
    ).outerjoin(Rating, Book.book_id == Rating.book_id) \
     .group_by(Book.book_id) \
     .all()

    
    books = [{
        'book': book,
        'avg_rating': avg_rating,
        'feedback_list': (feedback_list or '').split(',') 
    } for book, avg_rating, feedback_list in books_with_ratings_and_feedback]

    return render_template('admin_books.html', title='Books', books=books)


@app.route("/admin/requests")
@admin_required
def admin_requests():
    requests = db.session.query(BookRequest, User.username, Book.name)\
        .join(User, BookRequest.user_id == User.user_id)\
        .join(Book, BookRequest.book_id == Book.book_id)\
        .all()
    
    
    issued_books = db.session.query(IssuedBook, User.username, Book.name)\
        .join(User, IssuedBook.user_id == User.user_id)\
        .join(Book, IssuedBook.book_id == Book.book_id)\
        .all()
    return render_template('admin_requests.html', title='Requests', requests=requests, issued_books=issued_books)


@app.route("/admin/requests/<int:request_id>/approve")
@admin_required
def approve_request(request_id):
    request = BookRequest.query.get(request_id)
    if request:
        book = Book.query.get(request.book_id)
        if book:
            issued_book = IssuedBook(user_id=request.user_id, book_id=request.book_id, return_date=request.return_date)
            db.session.add(issued_book)
            db.session.delete(request)
            db.session.commit()
            flash('Request approved successfully', 'success')
            return redirect(url_for('admin_requests'))
        else:
            flash('Book not found', 'danger')
            return redirect(url_for('admin_requests'))
    else:
        flash('Request not found', 'danger')
        return redirect(url_for('admin_requests'))


@app.route("/admin/requests/<int:request_id>/reject")
@admin_required
def reject_request(request_id):
    request = BookRequest.query.get(request_id)
    if request:
        db.session.delete(request)
        db.session.commit()
        flash('Request rejected successfully', 'success')
        return redirect(url_for('admin_requests'))
    else:
        flash('Request not found', 'danger')
        return redirect(url_for('admin_requests'))


@app.route("/admin/issued_books/<int:issued_id>/revoke")
@admin_required
def revoke_issued_book(issued_id):
    issued_book = IssuedBook.query.get(issued_id)
    if issued_book:
        db.session.delete(issued_book)
        db.session.commit()
        flash('Issued book revoked successfully', 'success')
        return redirect(url_for('admin_books'))
    else:
        flash('Issued book not found', 'danger')
        return redirect(url_for('admin_books'))
    
@app.route("/admin/statistics")
@admin_required
def admin_statistics():
    total_books = Book.query.count()
    total_sections = Section.query.count()
    total_requests = BookRequest.query.count()
    total_issued_books = IssuedBook.query.count()
    total_users = User.query.count()
    total_ratings = Rating.query.count()
    rated_books = db.session.query(Book, Rating.rating).join(Rating, Book.book_id == Rating.book_id).all()
    
    
    ratings = db.session.query(Book.name, func.avg(Rating.rating),Rating.feedback).join(Rating, Book.book_id == Rating.book_id).group_by(Book.name).all()
    book_names = [rating[0] for rating in ratings]
    avg_ratings = [rating[1] for rating in ratings]
    
    
    plt.figure(figsize=(10, 6))
    plt.bar(book_names, avg_ratings, color='skyblue')
    plt.xlabel('Book Name')
    plt.ylabel('Average Rating')
    plt.title('Average Ratings for Books')
    plt.xticks(rotation=45, ha='right') 
    plt.tight_layout()  
    plt.savefig('static/images/average_ratings_chart.png')
    return render_template('admin_statistics.html', title='Statistics', total_books=total_books, total_sections=total_sections, total_requests=total_requests, total_issued_books=total_issued_books, total_users=total_users, total_ratings=total_ratings, rated_books=rated_books, ratings=ratings)


@app.route("/admin/search", methods=['GET', 'POST'])
@admin_required
def admin_search():
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
        return render_template('admin_search_results.html', title='Search', sections=sections, books=books, query=query)
    return render_template('admin_search_form.html', title='Search', form=form)
