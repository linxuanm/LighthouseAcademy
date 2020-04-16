import os


PATH = '../static/images/'


def get_image(id_code: str, question_type):
    file_path = os.path.join(PATH + question_type + "/", id_code + '.png')
    print(file_path)
    return file_path


def save_image(file, question_id: str):
    if file.filename == '':
        return

    file.save(os.path.join(PATH, question_id + '.png'))
