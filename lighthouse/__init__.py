from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import config


app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)
db.app = app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

from lighthouse import views  # noqa: F401,E402
