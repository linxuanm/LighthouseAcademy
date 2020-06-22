from lighthouse import app
from flask import render_template


@app.route('/generate_paper', methods=['GET', 'POST'])
def generate_paper():
    return render_template('generate_paper.html', title='Generate Papers')
