from flask import jsonify, render_template

def delete_questions_without_field(questions, field_array, field: str):
    '''
    Take an array of questions, check if one of their field (field) is in the provided array (field_array).
    Delete those that do not
    '''
    index = 0
    index_list = []
    for i in questions:
        if i.asdict().get(field) not in field_array:
            index_list.append(index)
        index += 1
    processed_questions = [i for j, i in enumerate(questions) if j not in index_list]
    return processed_questions

def search_error_response(message: str):
    return render_template(
        'search.html',
        title='Search Error',
        error_message=message
    )

