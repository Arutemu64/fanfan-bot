from flask import Flask

from src.config import conf
from src.panel import admin, db, env, login_manager, views
from src.panel.login import login_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = conf.db.build_connection_str(
        driver="psycopg"
    )
    app.config["SECRET_KEY"] = env("SECRET_KEY")
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(login_bp)

    admin.init_app(app)
    views.add_views(db, admin)

    return app


def main():
    create_app().run(debug=env.bool("DEBUG"))


if __name__ == "__main__" and conf.bot.mode == "polling":
    main()
