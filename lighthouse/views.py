from lighthouse import app, db, login_manager
from lighthouse.models import User, Question, Sub_Question, Mark
from lighthouse.db_helper import db_entry_exists, str2bool
from lighthouse.interactions import (
	info,
	error,
	verify_email_request,
	render_user_template,
	redirect_to
)

from constants import EMAIL_REGEX

import os
import re
from flask import render_template, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash


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


@app.route('/login', methods=['GET','POST'])
def login():
	return render_template('login.html', title='Login')

@app.route('/add_questions_to_question_bank', methods=['GET'])
def add_questions_to_question_bank():
	return render_template(
		'add_questions_to_question_bank.html',
		title='Add Questions to the Question Bank'
	)

@app.route('/add_qs', methods=['POST'])
def add_qs():
	data = request.form.to_dict()

	for key in data:
		if "questions" in key and "text" in key and "sub" not in key:
			series_id = key[0:-6]
			id_code = data.get("{}[id_code]".format(series_id))
			if db_entry_exists(Question, id_code=id_code):
				return {"code":2,"content":"One of the Question ID Exists in DataBase"}, 200

			question = Question(data.get(key), data.get("{}[id_code]".format(series_id)), str2bool(data.get("{}[has_image]".format(series_id))), str2bool(data.get("{}[has_subquestion]".format(series_id))))
			db.session.add(question)
			db.session.commit()

	for key in data:
		if "sub_questions" in key and "text" in key:
			series_id = key[0:-6]
			main_question_id_code = data.get("{}[main_question_id_code]".format(series_id))
			main_question = Question.query.filter_by(id_code = main_question_id_code).first()
			main_question_id = main_question.id

			sub_question = Sub_Question(data.get(key), data.get("{}[id_code]".format(series_id)), str2bool(data.get("{}[has_image]".format(series_id))), main_question_id, int(data.get("{}[sub_question_number]".format(series_id))))
			db.session.add(sub_question)
			db.session.commit()

	for key in data:
		if "mark" in key and "text" in key:
			series_id = key[0:-6]
			main_question_id_code = data.get("{}[id_code]".format(series_id))
			for_sub_question = int(data.get("{}[for_sub_question]".format(series_id)))
			if for_sub_question == 0:
				question = Question.query.filter_by(id_code = main_question_id_code).first()
				question_id = question.id
				for_sub_question = False
			else:
				question = Sub_Question.query.filter_by(id_code = data.get("{}[id_code]".format(series_id)), sub_question_number = for_sub_question).first()
				question_id = question.id
				for_sub_question = True

			mark = Mark(data.get(key), data.get("{}[mark]".format(series_id)), data.get("{}[id_code]".format(series_id)), question_id, int(data.get("{}[order]".format(series_id))), for_sub_question)
			db.session.add(mark)
			db.session.commit()

	return {"code":5,"content":"hi"}, 200

@app.route('/upload_image', methods=['POST'])
def upload_image():
	uploaded_image = request.files.get('file');
	uploaded_id_code = request.form.get('id_code');
	uploaded_for_sub = int(request.form.get('for_sub_question'));
	dirname = os.path.dirname(__file__)
	if uploaded_for_sub == 0:
		question = Question.query.filter_by(id_code = uploaded_id_code).first()
		question_id = question.id
		uploaded_image.save(os.path.join(dirname, "static/images/questions", str(question_id) + ".png"))
	else:
		print(uploaded_for_sub)
		question = Sub_Question.query.filter_by(id_code = uploaded_id_code, sub_question_number = uploaded_for_sub).first()
		question_id = question.id
		uploaded_image.save(os.path.join(dirname, "static/images/sub_questions", str(question_id) + ".png"))
	return "hi"

@app.route('/search', methods=['GET'])
def search():
	return render_template('search.html', title='Search for a Question')

@app.route('/generate_paper', methods=['GET'])
def generate_paper():
	return render_template('generate_paper.html', title='Generate Papers')

@app.route('/preview_paper', methods=['GET'])
def preivew_paper():
	return render_template('preview_paper.html', title='Preview Paper')

@app.route('/user/<user_id>')
def user(user_id):
	user = User.query.filter_by(username=user_id).first()
	if user is None:
		# TODO: make it more obvious to the user that the user does not exists
		return redirect(url_for('home'))

	if user.is_verified():
 		return render_user_template(user_id)

	return verify_email_request(user.email)


@app.route('/verify/<verify_key>')
def verify(verify_key):
 	user = User.query.filter_by(verify_key=verify_key).first()
 	if user is None:
 		return redirect(url_for('home'))

 	if user.is_verified():
 		return render_user_template(user_id)

 	user.verify_key = ''
 	db.session.commit()

 	return render_template(
 		'info.html',
 		title='Account activation',
 		header='Account activated',
 		sections=[
 			'Your account has been activated successfully.',
 			f'<a href=\'/user/{user.username}\'>Click here</a> to access '
 			'your profile page.'
 		]
 	)
 	# TODO: add the thingy that tells the user the thingy


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)
