from lighthouse import db
from lighthouse.image_loader import get_image

import time
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
	text = db.Column(db.String(80), nullable=False)
	id_code = db.Column(db.String(80), nullable=False)
	has_image = db.Column(db.Boolean(), nullable=False)
	has_subquestion = db.Column(db.Boolean(), nullable=False)

	def __init__(self, text, id_code, has_image, has_subquestion):
		self.text = text
		self.id_code = id_code
		self.has_image = has_image
		self.has_subquestion = has_subquestion

	def get_image_path(self):
		return get_image(self.id, "questions")


class Sub_Question(db.Model):

	__tablename__ = 'sub_questions'

	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(80), nullable=False)
	id_code = db.Column(db.String(40), nullable=False)
	has_image = db.Column(db.Boolean(), nullable=False)
	main_question_id = db.Column(db.Integer, nullable=False)
	sub_question_number = db.Column(db.Integer, nullable=False)

	def __init__(self, text, id_code, has_image, main_question_id, sub_question_number):
		self.text = text
		self.has_image = has_image
		self.main_question_id = main_question_id
		self.id_code = id_code
		self.sub_question_number = sub_question_number

	def get_image_path(self):
		return get_image(self.id, "sub_questions")

class Mark(db.Model):

	__tablename__ = 'mark'

	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(80), nullable=False)
	id_code = db.Column(db.String(40), nullable=False)
	mark = db.Column(db.String(10), nullable=False)
	question_id = db.Column(db.String(40), nullable=False)
	order = db.Column(db.Integer, nullable=False)
	for_sub_question = db.Column(db.Boolean(), nullable=False)


	def __init__(self, text, mark, id_code, question_id, order, for_sub_question):
		self.text = text
		self.mark = mark
		self.question_id = question_id
		self.order = order
		self.id_code = id_code
		self.for_sub_question = for_sub_question


db.create_all()
