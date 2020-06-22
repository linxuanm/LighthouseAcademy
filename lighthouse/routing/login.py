from lighthouse import app
from flask import render_template


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Login')
