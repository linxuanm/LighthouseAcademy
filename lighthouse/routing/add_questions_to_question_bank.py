from flask import render_template, request, jsonify
from lighthouse import app, db
from lighthouse.models import Question, Sub_Question, Question_Mark, Sub_Question_Mark

import os
import json


@app.route('/add_qs', methods=['POST'])
def add_qs():

    data = json.loads(request.form['data'])

    new_question = Question(data["question"]["text"], data["question"]["id_code"], data["question"]["has_image"])

    # Marks for the main question
    marks = data["question"]["marks"]
    for key, value in marks.items():
        db.session.add(Question_Mark(value["text"], value["credit"], key, value["has_image"], new_question))

    sub_questions = data["question"]["sub_questions"]
    for key, value in sub_questions.items():
        new_sub_question = Sub_Question(value["text"], value["id_code"], value["has_image"], new_question)
        db.session.add(new_sub_question)
        sub_question_marks = value["marks"]
        for index, content in sub_question_marks.items():
            db.session.add(Sub_Question_Mark(content["text"], content["credit"], index, content["has_image"], new_sub_question))

    db.session.commit()

    return jsonify({'code': 5})


@app.route('/upload_image', methods=['POST'])
def upload_image():
    dirname = os.path.dirname(__file__)

    files = request.files.getlist('files')
    id_codes = request.form.get('id_codes').split(',')
    orders = request.form.get('orders').split(',')

    for file, id_code, order in zip(files, id_codes, orders):
        if order != "none":
            file.save(os.path.join(dirname, "../static/images/marks", str(id_code) + " " + order + ".png"))
        else:
            file.save(os.path.join(dirname, "../static/images/questions", str(id_code) + ".png"))

    return jsonify({"image_upload": "success"})


@app.route('/add_questions_to_question_bank', methods=['GET'])
def add_questions_to_question_bank():
    return render_template(
        'add_questions_to_question_bank.html',
        title='Add Questions to the Question Bank'
    )
