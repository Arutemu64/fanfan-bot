import flask
import jwt
from environs import Env
from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy

from src.bot.structures import UserRole
from src.config import conf
from src.db.models import Base, User
from src.panel.views import add_views

env = Env()

app = Flask(__name__)
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
admin = Admin(app, name="ff-bot", template_mode="bootstrap4", url="/")

app.config["SQLALCHEMY_DATABASE_URI"] = conf.db.build_connection_str(driver="psycopg")
app.config["SECRET_KEY"] = env("SECRET_KEY")

db.init_app(app)
login_manager.init_app(app)
add_views(db, admin)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route("/login", methods=["GET"])
def login():
    jwt_token = flask.request.args.get("token")
    jwt_decoded = jwt.decode(
        jwt=jwt_token,
        key=app.config["SECRET_KEY"],
        algorithms=["HS256"],
    )
    user: User = db.session.get(User, jwt_decoded["user_id"])
    if user.role == UserRole.ORG:
        login_user(user)
        flask.flash("Вы успешно вошли.", category="success")
        return flask.redirect(flask.url_for("admin.index"))
    else:
        flask.flash("Веб-панель доступна только организаторам!", category="danger")
        return flask.redirect(flask.url_for("admin.index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flask.flash("Вы вышли из учётной записи.")
    return flask.redirect(flask.url_for("admin.index"))


def main():
    app.run(debug=env.bool("DEBUG"))


if __name__ == "__main__" and conf.bot.mode == "polling":
    main()
