from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads


# Globally accessible libraries
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
datafiles = UploadSet("datafiles", extensions=["xls"])


def init_db():
    # Create sql tables for our date models
    from .models import (
        User,
        Relationship,
        Call,
        Meeting,
        SLACall,
        SLAMeeting,
        LMAAccount,
        SMAAccount,
        UpdateAccount,
        InvResp,
        TAOfficer,
        Access,
        Month,
        populate_db,
    )

    # db.drop_all()
    # db.create_all()
    if Access.query.get(1) == None:
        populate_db()


def create_app():
    """Initalize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.DevConfig")

    # Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    configure_uploads(app, datafiles)

    with app.app_context():
        # Include our Routes
        from . import routes
        from .main import routes as main
        from .auth import routes as auth
        from .data import routes as data
        from .relationship import routes as relationship
        from .reports import routes as reports

        # Import template_filters
        from .modules import custom_template_filters

        # Uncomment to reset database.
        # init_db()

        # Register Blueprints
        app.register_blueprint(main.main_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(data.data_bp)
        app.register_blueprint(relationship.rel_bp)
        app.register_blueprint(reports.reports_bp)

        return app
