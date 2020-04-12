def db_entry_exists(db, **kwargs):
	'''
	Checks whether an entry that matches the criteria exists in the given db.

	i.e. db_entry_exists(User, username="johnny") will return if there is an
	entry in the db "User" whose username is "johnny".
	'''
	return db.query.filter_by(**kwargs).count()

def str2bool(v):
	'''
	Turns "True" to true and "False" to false
	'''
	return v.lower() in ("yes", "true", "t", "1")

def delete_questions_without_field(questions, field_array, field):
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