from lighthouse import db
from lighthouse.image_loader import get_image

import time
import re
from constants import MARK_GROUPING_REGEX
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
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


class Base_Question():
    text = db.Column(db.String(400), nullable=False)
    id_code = db.Column(db.String(40), nullable=False)
    has_image = db.Column(db.Boolean(), nullable=False)

    attr_subject = db.Column(db.String(20), nullable=False)
    attr_season = db.Column(db.String(5), nullable=False)
    attr_year = db.Column(db.String(10), nullable=False)
    attr_paper = db.Column(db.String(5), nullable=False)
    attr_question = db.Column(db.String(5), nullable=False)
    attr_maxMark = db.Column(db.String(5), nullable=False)
    attr_chapter = db.Column(db.String(5), nullable=False)
    attr_difficulty = db.Column(db.String(10), nullable=False)
    attr_timeZone = db.Column(db.String(5), nullable=False)

    def __init__(self, text, id_code, has_image):
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
        self.attr_subject = subject
        self.attr_difficulty = difficulty
        self.attr_season = season
        self.attr_year = '20{}'.format(id_code[1:3])
        self.attr_paper = re.search(r'(?:-(\w+)){2}', id_code).group(1)
        self.attr_question = re.search(r'(?:-(\w+)){3}', id_code).group(1)
        self.attr_maxMark = re.search(r'(?:-(\w+)){5}', id_code).group(1)
        self.attr_chapter = re.search(r'(?:-(\w+)){6}', id_code).group(1)
        self.attr_timeZone = re.search(r'(?:-(\w+)){8}', id_code).group(1)

    def get_image_path(self):
        return get_image(self.id_code, "questions")

    # Get all attr_x as dict
    def asdict(self):
        return {
            "attr_subject": self.attr_subject,
            "attr_season": self.attr_season,
            "attr_year": self.attr_year,
            "attr_paper": self.attr_paper,
            "attr_question": self.attr_question,
            "attr_maxMark": self.attr_maxMark,
            "attr_chapter": self.attr_chapter,
            "attr_difficulty": self.attr_difficulty
        }


class Question(Base_Question, db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    sub_questions = relationship("Sub_Question", back_populates="parent_question")
    marks = relationship("Question_Mark", back_populates="question")

    def __init__(self, text, id_code, has_image):
        super().__init__(text, id_code, has_image)


class Sub_Question(Base_Question, db.Model):

    __tablename__ = 'sub_question'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, ForeignKey("question.id"))
    parent_question = relationship("Question", back_populates="sub_questions")
    marks = relationship("Sub_Question_Mark", back_populates="question")

    def __init__(self, text, id_code, has_image, parent_question):
        super().__init__(text, id_code, has_image)
        self.parent_question = parent_question

    def get_parent_question(self):
        return Question.query.filter_by(id=self.main_question_id).first()


class Base_Mark():

    text = db.Column(db.String(300), nullable=False)
    mark = db.Column(db.String(10), nullable=False)
    has_image = db.Column(db.Boolean(), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    def __init__(self, text, mark, order, has_image):
        self.text = text
        self.mark = mark
        self.order = order
        self.has_image = has_image

    def get_maxMark(self):
        totalmark = 0
        for i in re.findall(MARK_GROUPING_REGEX, self.mark):
            totalmark = totalmark + int(i)
        return totalmark


class Question_Mark(Base_Mark, db.Model):

    __tablename__ = 'question_mark'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, ForeignKey("question.id"))
    question = relationship("Question", back_populates="marks")

    def __init__(self, text, mark, order, has_image, question):
        super().__init__(text, mark, order, has_image)
        self.question = question


class Sub_Question_Mark(Base_Mark, db.Model):

    __tablename__ = 'sub_question_mark'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, ForeignKey("sub_question.id"))
    question = relationship("Sub_Question", back_populates="marks")

    def __init__(self, text, mark, order, has_image, sub_question):
        super().__init__(text, mark, order, has_image)
        self.question = sub_question


db.create_all()
