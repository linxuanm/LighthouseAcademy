from lighthouse import app
from lighthouse.models import Question, Sub_Question
from lighthouse.interactions import http_error_response
from flask import render_template, request
import json


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
