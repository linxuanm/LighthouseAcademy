from lighthouse import app, db, login_manager
from lighthouse.models import User, Question, Sub_Question, Mark
from lighthouse.db_helper import (
    db_entry_exists,
    str2bool,
)
from lighthouse.interactions import (
    error,
    verify_email_request,
    render_user_template,
    redirect_to,
    http_error_response
)
from lighthouse.search_page_helper import (
    delete_questions_without_field,
    search_error_response,
)
from constants import (
    EMAIL_REGEX,
    QUESTION_ID_CODE_REGEX,
    MARK_REGEX,
    SEARCH_RESULT_MAX
)

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


@app.route('/login', methods=['GET', 'POST'])
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
    # Do a server side check on whether the sent data is valid
    for key, item in data.items():
        if item is None or not item:
            return error("Input field cannot be empty!")
        if "id_code" in key:
            if not re.match(QUESTION_ID_CODE_REGEX, item):
                return error("Invalid Question ID Input! Please Contact the Admin")
            if db_entry_exists(Question, id_code=item):
                return error("One of the Question ID Exists in Question Bank")
        if "[mark]" in key:
            if not re.match(MARK_REGEX, item):
                return error("Invalid Marks Input! Please Contact the Admin")

    # Then insert data into database
    new_questions = []
    for key in data:
        if "questions" in key and "text" in key and "sub" not in key:
            series_id = key[0:-6]
            new_questions.append(
                Question(
                    data.get(key),
                    data.get("{}[id_code]".format(series_id)),
                    str2bool(data.get("{}[has_image]".format(series_id))),
                    str2bool(data.get("{}[has_subquestion]".format(series_id)))
                )
            )
    for i in new_questions:
        db.session.add(i)
    db.session.flush()

    new_sub_questions = []
    for key in data:
        if "sub_questions" in key and "text" in key:
            series_id = key[0:-6]
            main_question_id_code = data.get("{}[main_question_id_code]".format(series_id))

            # Get this sub_questions' main question id code
            main_question = Question.query.filter_by(id_code=main_question_id_code).first()
            main_question_id = main_question.id

            new_sub_questions.append(
                Sub_Question(
                    data.get(key),
                    data.get("{}[id_code]".format(series_id)),
                    str2bool(data.get("{}[has_image]".format(series_id))),
                    main_question_id
                )
            )
    for i in new_sub_questions:
        db.session.add(i)
    db.session.flush()

    new_marks = []
    for key in data:
        if "mark" in key and "text" in key:
            series_id = key[0:-6]
            new_marks.append(
                Mark(
                    data.get(key),
                    data.get("{}[mark]".format(series_id)),
                    data.get("{}[id_code]".format(series_id)),
                    int(data.get("{}[order]".format(series_id))),
                    str2bool(data.get("{}[has_image]".format(series_id))),
                )
            )
    for i in new_marks:
        db.session.add(i)

    db.session.commit()

    return jsonify({'code': 5})


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if request.form.get('has_no_image'):
        return jsonify({"code": 1})
    dirname = os.path.dirname(__file__)

    files = request.files.getlist('files')
    id_codes = request.form.get('id_codes').split(',')
    orders = request.form.get('orders').split(',')

    for file, id_code, order in zip(files, id_codes, orders):
        if order != "none":
            file.save(os.path.join(dirname, "static/images/marks", str(id_code) + " " + order + ".png"))
        else:
            if int(re.search(r'(?:-(\w+)){4}', id_code).group(1)) == 0:
                file.save(os.path.join(dirname, "static/images/questions", str(id_code) + ".png"))
            else:
                file.save(os.path.join(dirname, "static/images/sub_questions", str(id_code) + ".png"))

    return jsonify({"code": 1})


@app.route('/search', methods=['GET', 'POST'])
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

    # Filter queried question
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

    # Ascertain current page
    if request.args.get("page"):
        current_page = request.args.get("page")
        if current_page.isdigit():
            current_page = int(current_page)
            if current_page <= 0:
                return search_error_response("Page Number Cannot be 0 or Negative")
        else:
            return search_error_response("Invalid Result Page Number")
    else:
        current_page = 1

    # Calculate the number of total page
    total_page = len(questions) // SEARCH_RESULT_MAX + 1

    # Divide questions into sections according to current page. (Else the user has to load the entire database at one go)
    questions = questions[(current_page-1)*SEARCH_RESULT_MAX:(current_page-1)*SEARCH_RESULT_MAX+SEARCH_RESULT_MAX]

    # Get sub-questions and marks
    # Meanwhile check if no matching question can be found and return message
    sub_questions = []
    marks = []
    if len(questions) != 0:
        for i in questions:
            if i.has_subquestion:
                sub_questions.extend(Sub_Question.query.filter_by(main_question_id=i.id).all())
            marks.extend(Mark.query.filter_by(id_code=i.id_code).all())
        for i in sub_questions:
            marks.extend(Mark.query.filter_by(id_code=i.id_code).all())

    else:
        return search_error_response("Lighthouse Cannot Find Any Question Text or ID That Contains Your Seach")

    return render_template(
        'search.html',
        title='Search for Question',
        questions=questions,
        sub_questions=sub_questions,
        marks=marks,
        current_page=current_page,
        total_page=total_page
    )


@app.route('/delete_selected', methods=['POST'])
def delete_questions():
    # IMPORTANT TO DO:
    # CHECK IF USER REALLY HAS THE RIGHT TO DELETE QUESTION!!!
    if request.method == 'POST':
        if request.cookies.get('selected_questions'):
            selected_questions = json.loads(request.cookies.get('selected_questions'))
            for i in selected_questions:
                question = Question.query.filter_by(id_code=i).first()
                if question is not None and question:
                    db.session.delete(question)

        if request.cookies.get('selected_sub_questions'):
            selected_sub_questions = json.loads(request.cookies.get('selected_sub_questions'))
            for i in selected_sub_questions:
                sub_question = Sub_Question.query.filter_by(id_code=i).first()
                if sub_question is not None and sub_question:
                    db.session.delete(sub_question)

        if request.cookies.get('selected_marks'):
            selected_marks = json.loads(request.cookies.get('selected_marks'))
            for i in selected_marks:
                mark = Mark.query.filter_by(id=i).first()
                if mark is not None and mark:
                    db.session.delete(mark)

        db.session.commit()

        return jsonify({"code": 3})
    return http_error_response(402)


@app.route('/generate_paper', methods=['GET', 'POST'])
def generate_paper():

    return render_template('generate_paper.html', title='Generate Papers')


@app.route('/preview_paper', methods=['GET', 'POST'])
def preview_paper():
    selected_questions = json.loads(request.cookies.get('selected_questions'))
    questions = []
    for i in selected_questions:
        questions.append(Question.query.filter_by(id_code=i).first())
    selected_sub_questions = json.loads(request.cookies.get('selected_sub_questions'))
    sub_questions = []
    for i in selected_sub_questions:
        sub_questions.append(Sub_Question.query.filter_by(id_code=i).first())

    # Get max mark
    total_mark = 0
    for i in questions:
        for j in i.get_all_mark():
            total_mark += j.get_maxMark()
    for i in sub_questions:
        for j in i.get_all_mark():
            total_mark += j.get_maxMark()

    if len(questions) == 0 and len(sub_questions) == 0:
        return http_error_response(401)
    else:
        return render_template('preview_paper.html', title='Preview Paper', questions=questions, sub_questions=sub_questions, total_mark=total_mark)


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
        return render_user_template(user.id)

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
