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
