import flask
import jwt
from flask import Blueprint, current_app
from flask_login import login_required, login_user, logout_user

from src.bot.structures import UserRole
from src.db.models import User
from src.panel import db, login_manager

login_bp = Blueprint("routes", __name__)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@login_bp.route("/login", methods=["GET"])
def login():
    jwt_token = flask.request.args.get("token")
    jwt_decoded = jwt.decode(
        jwt=jwt_token,
        key=current_app.config["SECRET_KEY"],
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


@login_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flask.flash("Вы вышли из учётной записи.")
    return flask.redirect(flask.url_for("admin.index"))
