from lighthouse import db, app
from lighthouse.models import User
from lighthouse.interactions import verify_email_request, render_user_template
from flask import render_template, redirect, url_for


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
