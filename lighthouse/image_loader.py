import os


PATH = 'static/images/'


def get_image(question_id: str, question_type):
	file_path = os.path.join(PATH + question_type, question_id + '.png')
	return file_path if (os.path.isfile(file_path)) else None


def save_image(file, question_id: str):
	if file.filename == '':
		return

	file.save(os.path.join(PATH, question_id + '.png'))
