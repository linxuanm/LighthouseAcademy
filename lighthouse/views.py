from lighthouse import app, db, login_manager
from lighthouse.models import User, Question, Sub_Question, Mark
from lighthouse.db_helper import db_entry_exists, str2bool, delete_questions_without_field
from lighthouse.interactions import (
	info,
	error,
	verify_email_request,
	render_user_template,
	redirect_to,
	search_error_response,
)

from constants import EMAIL_REGEX, QUESTION_ID_CODE_REGEX, MARK_REGEX

import os
import re
import json
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

	#Do a server side check on whether the sent data is valid
	all_id_code = []
	all_mark = []
	for key in data:
		if "questions" in key and "text" in key and "sub" not in key:
			series_id = key[0:-6]
			all_id_code.append(data.get("{}[id_code]".format(series_id)))
	for key in data:
		if "sub_questions" in key and "text" in key:
			series_id = key[0:-6]
			all_id_code.append(data.get("{}[id_code]".format(series_id)))
	for key in data:
		if "mark" in key and "text" in key:
			series_id = key[0:-6]
			all_id_code.append(data.get("{}[id_code]".format(series_id)))
			all_mark.append(data.get("{}[mark]".format(series_id)))

	for i in all_id_code:
		if not re.match(QUESTION_ID_CODE_REGEX, i):
			return error("Invalid Question ID Input! Please Contact the Admin")
		if db_entry_exists(Question, id_code=i):
			return error("One of the Question ID Exists in Question Bank")
	for i in all_mark:
		if not re.match(MARK_REGEX, i):
			return error("Invalid Marks Input! Please Contact the Admin")

	# Then insert data into database
	new_question = []
	for key in data:
		if "questions" in key and "text" in key and "sub" not in key:
			series_id = key[0:-6]
			id_code = data.get("{}[id_code]".format(series_id))
			if not re.match(QUESTION_ID_CODE_REGEX, id_code):
				return error("Invalid Input! Please Contact the Admin")
			if db_entry_exists(Question, id_code=id_code):
				return error("One of the Question ID Exists in Question Bank")

			question = Question(
				data.get(key), 
				data.get("{}[id_code]".format(series_id)), 
				str2bool(data.get("{}[has_image]".format(series_id))), 
				str2bool(data.get("{}[has_subquestion]".format(series_id)))
				)
			new_question.append(question)
	for i in new_question:
		db.session.add(i)
	db.session.commit()

	new_sub_question = []
	for key in data:
		if "sub_questions" in key and "text" in key:
			series_id = key[0:-6]
			main_question_id_code = data.get("{}[main_question_id_code]".format(series_id))
			main_question = Question.query.filter_by(id_code = main_question_id_code).first()
			main_question_id = main_question.id

			sub_question = Sub_Question(
				data.get(key), 
				data.get("{}[id_code]".format(series_id)), 
				str2bool(data.get("{}[has_image]".format(series_id))), 
				main_question_id, int(data.get("{}[sub_question_number]".format(series_id)))
				)
			new_sub_question.append(sub_question)
	for i in new_sub_question:
		db.session.add(i)
	db.session.commit()

	new_mark = []
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
			mark = Mark(data.get(key), 
				data.get("{}[mark]".format(series_id)), 
				data.get("{}[id_code]".format(series_id)), 
				question_id, int(data.get("{}[order]".format(series_id))), 
				for_sub_question
				)
			new_mark.append(mark)
	for i in new_mark:
		db.session.add(i)
	db.session.commit()


	return jsonify({'code':5})

@app.route('/upload_image', methods=['POST'])
def upload_image():
	file = request.files.get('file');
	id_code = request.form.get('id_code');
	for_sub_question = int(request.form.get('for_sub_question'));
	dirname = os.path.dirname(__file__)
	if for_sub_question == 0:
		file.save(os.path.join(dirname, "static/images/questions", str(id_code) + ".png"))
	else:
		question = Sub_Question.query.filter_by(id_code = id_code, sub_question_number = for_sub_question).first()
		question_id = question.id
		file.save(os.path.join(dirname, "static/images/sub_questions", str(id_code) + ".png"))
	return "hi"

@app.route('/search', methods=['GET','POST'])
def search():
	if request.args.get("search") == '' or not request.args.get("search"):
		questions = Question.query.all()
	else:
		user_query = request.args.get("search")
		formated_query = '%' + user_query + '%'
		questions = Question.query.filter(Question.text.like(formated_query) | Question.id_code.like(formated_query)).all()
		queried_sub_questions = Sub_Question.query.filter(Sub_Question.text.like(formated_query) | Sub_Question.id_code.like(formated_query)).all()

		queried_sub_questions_main_question = []
		for i in queried_sub_questions:
			queried_sub_questions_main_question.append(i.get_main_question())
		questions = list(set(questions) | set(queried_sub_questions_main_question))

	#Filter queried question
	if request.args.get("season"):
		filter_season = request.args.get("season").split(",")
		questions = delete_questions_without_field(questions, filter_season, "attr_season")
	if request.args.get("paper"):
		filter_paper = request.args.get("paper").split(",")
		questions = delete_questions_without_field(questions, filter_paper, "attr_paper")
	if request.args.get("chapter"):
		filter_chapter = request.args.get("chapter").split(",")
		questions = delete_questions_without_field(questions, filter_chapter, "attr_chapter")
	if request.args.get("difficulty"):
		filter_difficulty = request.args.get("difficulty").split(",")
		questions = delete_questions_without_field(questions, filter_difficulty, "attr_difficulty")

	#Ascertain current page
	if request.args.get("page"):
		current_page = request.args.get("page")
		if current_page.isdigit():
			current_page=int(current_page)
			if current_page <= 0:
				return search_error_response("Page Number Cannot be 0 or Negative")
		else:
			return search_error_response("Invalid Result Page Number")
	else:
		current_page = 1

	max_display = 10 #max number of questions in one page

	#Calculate the number of total page
	total_page = len(questions) // max_display + 1

	#Divide questions into sections according to current page. (Else the user has to load the entire database at one go)
	questions = questions[(current_page-1)*max_display:(current_page-1)*max_display+max_display]


	sub_questions = []
	if len(questions) != 0:
		for i in questions:
			if i.has_subquestion:
				sub_questions.extend(Sub_Question.query.filter_by(main_question_id=i.id).all())
	else:
		return search_error_response("Lighthouse Cannot Find Any Question Text or ID That Contains Your Seach")
	
	return render_template(
		'search.html', 
		title='Search for Question',
		questions=questions,
		sub_questions=sub_questions,
		current_page=current_page,
		total_page=total_page
		)

@app.route('/delete_questions', methods=['POST'])
def delete_questions():
	#IMPORTANT TO DO:
	#CHECK IF USER REALLY HAS THE RIGHT TO DELETE QUESTION!!!
	questions_to_delete = request.get_json()["questions"]
	sub_questions_to_delete = request.get_json()["sub_questions"]
	for i in questions_to_delete:
		question = Question.query.filter_by(id_code=i).first()
		if question is not None:
			db.session.delete(question)
	for i in sub_questions_to_delete:
		sub_question = Sub_Question.query.filter_by(id_code=i).first()
		if sub_question is not None:
			db.session.delete(sub_question)
	db.session.commit()
	return jsonify({"code":3})

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
