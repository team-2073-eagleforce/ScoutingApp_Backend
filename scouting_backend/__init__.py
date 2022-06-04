from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment
import os, sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)

    # assets = Environment()
    # assets.init_app(app)

    with app.app_context():
        # from .assets import compile_static_assets
        from .home import home
        from .retrieval import retrieval
        from .analysis import analysis

        app.register_blueprint(home.home_bp)
        app.register_blueprint(retrieval.retrieval_bp, url_prefix="/retrieval")
        app.register_blueprint(analysis.analysis_bp, url_prefic="/analysis")

        # Make sure that table no longer exists if you want to update columns
        db.create_all()

        # compile_static_assets(assets)

        return app
