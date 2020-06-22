from lighthouse import login_manager

# flake8: noqa: F403

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# from .search import *
from .home import *
from .login import *
from .add_questions_to_question_bank import *
from .preview_paper import *
from .generate_paper import *
from .user import *

from .test import *
