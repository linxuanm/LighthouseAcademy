from lighthouse import app, db
from lighthouse.models import Question, Sub_Question, Mark
from lighthouse.interactions import http_error_response, search_error_response
from flask import render_template, request, jsonify
from constants import (
    SEARCH_RESULT_MAX
)

import json


def delete_questions_without_field(questions: list, filters: dict):
    to_remove = []
    for key, value in filters.items():
        for question in questions:
            if not question.asdict().get(key) in value:
                to_remove.append(question)
    for question in to_remove:
        questions.remove(question)
    return questions


@app.route('/delete_selected', methods=['POST'])
def delete_questions():
    # TODO: CHECK IF THE USER REALLY HAS THE RIGHT TO DELETE QUESTION!!!
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
    filters = {}
    for f in ["season", "paper", "chapter", "difficulty"]:  # Available filters
        if request.args.get(f):
            filters.update({"attr_" + f: request.args.get(f).split(",")})
    if filters:
        questions = delete_questions_without_field(questions, filters)

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

    # Divide questions into sections according to current page. (Else the user has to load all the results at one go)
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
        return search_error_response("Lighthouse Cannot Find Any Question Text or ID That Contains Your Search")

    return render_template(
        'search.html',
        title='Search for Question',
        questions=questions,
        sub_questions=sub_questions,
        marks=marks,
        current_page=current_page,
        total_page=total_page
    )
