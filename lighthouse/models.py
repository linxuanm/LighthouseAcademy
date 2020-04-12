from lighthouse import db
from lighthouse.image_loader import get_image

import time
import re
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin, db.Model):
	'''Stores users' information.'''

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(40), nullable=False)
	username = db.Column(db.String(40), nullable=False)
	password = db.Column(db.String(40), nullable=False)
	rank = db.Column(db.String(20), default='User')
	verify_key = db.Column(db.String(40), default=False)
	register_time = db.Column(db.Float(), default=time.time())

	def __init__(self, email, username, password):
		self.email = email
		self.username = username
		self.password = generate_password_hash(password)
		self.verify_key = generate_password_hash(username + str(time.time()))

	def auth(self, password):
		return check_password_hash(self.password, password)

	def is_verified(self):
		'''
		Whether this account's associated email has been verified.
		If the account is not verified, self.verify_key will be the
		verification key; otherwise, self.verify_key will be empty.
		'''
		return not self.verify_key

	def __repr__(self):
		return str({
			'username': self.username,
			'email': self.email,
			'rank': self.rank,
		})


class Question(db.Model):

	__tablename__ = 'questions'

	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(200), nullable=False)
	id_code = db.Column(db.String(80), nullable=False)
	has_image = db.Column(db.Boolean(), nullable=False)
	has_subquestion = db.Column(db.Boolean(), nullable=False)
	attr_subject = db.Column(db.String(20), nullable=False)
	attr_season = db.Column(db.String(5), nullable=False)
	attr_year = db.Column(db.String(10), nullable=False)
	attr_paper = db.Column(db.String(5), nullable=False)
	attr_question = db.Column(db.String(5), nullable=False)
	attr_maxMark = db.Column(db.String(5), nullable=False)
	attr_chapter = db.Column(db.String(5), nullable=False)
	attr_difficulty = db.Column(db.String(10), nullable=False)

	def __init__(self, text, id_code, has_image, has_subquestion):
		if re.search(r'(?:-(\w+)){1}', id_code).group(1) == 'AddMat':
			subject = 'Additional Mathematics'
		if id_code[:1] == 'm':
			season = 'March'
		elif id_code[:1] == 's':
			season = 'May-June'
		else:
			season = 'November'
		if re.search(r'(?:-(\w+)){7}', id_code).group(1) == 'E':
			difficulty = 'Easy'
		elif re.search(r'(?:-(\w+)){7}', id_code).group(1) == 'M':
			difficulty = 'Medium'
		else:
			difficulty = 'Difficult'

		self.text = text
		self.id_code = id_code
		self.has_image = has_image
		self.has_subquestion = has_subquestion
		self.attr_subject = subject
		self.attr_difficulty = difficulty
		self.attr_season = season
		self.attr_year = '20{}'.format(id_code[1:3])
		self.attr_paper = re.search(r'(?:-(\w+)){2}', id_code).group(1)
		self.attr_question = re.search(r'(?:-(\w+)){3}', id_code).group(1)
		self.attr_maxMark= re.search(r'(?:-(\w+)){5}', id_code).group(1)
		self.attr_chapter = re.search(r'(?:-(\w+)){6}', id_code).group(1)

		

	def get_image_path(self):
		return get_image(self.id_code, "questions")

	def asdict(self):
		return {
		"attr_subject":self.attr_subject, 
		"attr_season":self.attr_season, 
		"attr_year":self.attr_year, 
		"attr_paper":self.attr_paper, 
		"attr_question": self.attr_question, 
		"attr_maxMark": self.attr_maxMark, 
		"attr_chapter": self.attr_chapter,
		"attr_difficulty": self.attr_difficulty
		}
	def get_all_mark(self):
		marks = []
		marks.extend(Mark.query.filter_by(id_code=self.id_code).all())
		return marks

class Sub_Question(db.Model):

	__tablename__ = 'sub_questions'

	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(80), nullable=False)
	id_code = db.Column(db.String(40), nullable=False)
	has_image = db.Column(db.Boolean(), nullable=False)
	main_question_id = db.Column(db.Integer, nullable=False)
	attr_subject = db.Column(db.String(20), nullable=False)
	attr_season = db.Column(db.String(5), nullable=False)
	attr_year = db.Column(db.String(10), nullable=False)
	attr_paper = db.Column(db.String(5), nullable=False)
	attr_question = db.Column(db.String(5), nullable=False)
	attr_subQuestion = db.Column(db.String(5), nullable=False)
	attr_maxMark = db.Column(db.String(5), nullable=False)
	attr_chapter = db.Column(db.String(5), nullable=False)
	attr_difficulty = db.Column(db.String(10), nullable=False)

	def __init__(self, text, id_code, has_image, main_question_id):
		if re.search(r'(?:-(\w+)){1}', id_code).group(1) == 'AddMat':
			subject = 'Additional Mathematics'
		if id_code[:1] == 'm':
			season = 'March'
		elif id_code[:1] == 's':
			season = 'May-June'
		else:
			season = 'November'
		if re.search(r'(?:-(\w+)){7}', id_code).group(1) == 'E':
			difficulty = 'Easy'
		elif re.search(r'(?:-(\w+)){7}', id_code).group(1) == 'M':
			difficulty = 'Medium'
		else:
			difficulty = 'Difficult'
		self.text = text
		self.id_code = id_code
		self.has_image = has_image
		self.main_question_id = main_question_id
		self.attr_subject = subject
		self.attr_difficulty = difficulty
		self.attr_season = season
		self.attr_year = '20{}'.format(id_code[1:3])
		self.attr_paper = re.search(r'(?:-(\w+)){2}', id_code).group(1)
		self.attr_question = re.search(r'(?:-(\w+)){3}', id_code).group(1)
		self.attr_subQuestion = re.search(r'(?:-(\w+)){4}', id_code).group(1)
		self.attr_maxMark= re.search(r'(?:-(\w+)){5}', id_code).group(1)
		self.attr_chapter = re.search(r'(?:-(\w+)){6}', id_code).group(1)

	def get_image_path(self):
		return get_image(self.id_code, "sub_questions")

	def get_main_question(self):
		return Question.query.filter_by(id=self.main_question_id).first()
	def get_all_mark(self):
		marks = []
		marks.extend(Mark.query.filter_by(id_code=self.id_code).all())
		return marks

class Mark(db.Model):

	__tablename__ = 'mark'

	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(80), nullable=False)
	id_code = db.Column(db.String(40), nullable=False)
	question_id = db.Column(db.Integer, nullable=False)
	mark = db.Column(db.String(10), nullable=False)
	has_image = db.Column(db.Boolean(), nullable=False)
	order = db.Column(db.Integer, nullable=False)
	attr_subQuestion = db.Column(db.String(5), nullable=False)


	def __init__(self, text, mark, id_code, order, has_image):
		self.text = text
		self.mark = mark
		self.order = order
		self.id_code = id_code
		self.has_image = has_image
		attr_subQuestion = re.search(r'(?:-(\w+)){4}', id_code).group(1)
		self.attr_subQuestion = attr_subQuestion

		if int(attr_subQuestion) == 0:
			self.question_id = Question.query.filter_by(id_code=id_code).first().id
		else:
			self.question_id = Sub_Question.query.filter_by(id_code=id_code).first().id

	def get_maxMark(self):
		pattern = r'(?<=[A-Z]){1,2}[0-9](?:\s|$)'
		totalmark = 0
		for i in re.findall(pattern, self.mark):
			totalmark = totalmark + int(i)
		return totalmark


db.create_all()
