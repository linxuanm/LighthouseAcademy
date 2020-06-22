from lighthouse import app, db
from flask import render_template, request
from lighthouse.models import User
from lighthouse.interactions import error, redirect_to
from lighthouse.db_helper import db_entry_exists
from constants import EMAIL_REGEX
from werkzeug.security import generate_password_hash
import re


@app.route('/')
def home():
    return render_template(
        'home.html',
        title='Lighthouse Academy',
        subjects=[
            'Chemistry', 'Physics', 'Mathematics', 'Computer Science',
            'Business', 'Economics', 'Biology', 'Art',
            'Music', 'Physical Education', 'History', 'Geography'
        ]
    )


@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if not all((email, username, password)):
        # There could be a dict key prob but let's just blame it on the user ;)
        return error('The entries cannot be blank.')

    if db_entry_exists(User, username=username):
        return error('That username is already taken.')

    if not re.match(EMAIL_REGEX, email):
        return error('Please enter a valid email.')

    if db_entry_exists(User, email=email):
        return error('That email is already taken.')

    hashed_pass = generate_password_hash(password)
    user = User(email, username, hashed_pass)
    db.session.add(user)
    db.session.commit()

    return redirect_to('/user/%s' % username)
