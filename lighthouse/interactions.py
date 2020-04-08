from flask import jsonify, render_template


def redirect_to(content):
	return jsonify({'code': 1, 'content': content})


def info(content):
	return jsonify({'code': 2, 'content': content})


def warning(content):
	return jsonify({'code': 3, 'content': content})


def error(content):
	return jsonify({'code': 4, 'content': content})


def render_user_template(user_id):
	return render_template(
		'user.html',
		user_id=user_id,
		title='About Me'
	)


def verify_email_request(email):
	return render_template(
		'info.html',
		title='Almost there...',
		header='Verify your email',
		sections=[
			'To activate your account, you need to verify your email.',
			'An email with the activation link has been sent to your email; \
			please check your email and click on the activation link.'
		]
	)


def http_error_response(error: int):
	return render_template(
		'info.html',
		title='Error: ' + str(error),
		header='There has been an error',
		sections=[
			f'An error has occured with error code {error} during \
			your request',
			'Please contact the Lighthouse team.'
		]
	)

def search_error_response(message: str):
	return render_template(
		'search.html',
		title="Search Error",
		error_message=message
		)



