from environs import Env
from flask_admin import Admin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from src.db import Base

env = Env()

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
admin = Admin(name="ff-bot", template_mode="bootstrap4", url="/")
