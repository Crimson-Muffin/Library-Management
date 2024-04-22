import os
import uuid
from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for
from models import IssuedBook
def user_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            flash('You need to be logged in to view this page', 'danger')
            return redirect(url_for('login'))
    return decorated_function

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            return func(*args, **kwargs)
        else:
            flash('You need to be an admin to view this page', 'danger')
            return redirect(url_for('admin_login'))
    return decorated_function


def has_permission(user, book):
    if user.is_admin:
        return True
    else:
        return has_issued_book(user, book)

def has_issued_book(user, book):
    return IssuedBook.query.filter_by(user_id=user.user_id, book_id=book.book_id).first() is not None

def save_pdf_file(pdf_file):
    random_string = str(uuid.uuid4().hex[:10])
    _, extension = os.path.splitext(pdf_file.filename)
    pdf_fn = f"{random_string}{extension}"
    current_file_path = os.path.abspath(__file__)
    root_path = os.path.abspath(os.path.join(current_file_path, '..', '..'))
    pdf_path = os.path.join(root_path, 'static', 'pdfs', pdf_fn)
    pdf_file.save(pdf_path)

    return pdf_fn


def delete_pdf_file(pdf_file):
    try:
        current_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','static', 'pdfs', pdf_file)
        os.remove(current_file_path)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        return False


