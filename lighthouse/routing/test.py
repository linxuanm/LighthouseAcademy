from lighthouse import app
from lighthouse.models import Question


@app.route('/test')
def test():
    question = Question.query.first()
    return question.sub_questions[0].marks[0].text
