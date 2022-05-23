from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads


# Globally accessible libraries
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
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
        CallMonth,
        MeetingMonth,
        populate_db,
        twelve_slas,
    )

    # db.drop_all()
    # db.create_all()
    if Access.query.get(1) == None:
        populate_db()
        db.session.commit()

    twelve_per_year = SLACall.query.filter_by(per_year=12).first()
    if len(twelve_per_year.months) != 12:
        twelve_slas()
        db.session.commit()


def create_app():
    """Initalize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.DevConfig")

    # Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    configure_uploads(app, datafiles)

    with app.app_context():
        # Include our Routes
        from pm_crm.errors.handlers import error_bp
        from pm_crm.main.routes import main_bp
        from pm_crm.auth.routes import auth_bp
        from pm_crm.data.routes import data_bp
        from pm_crm.relationship.routes import rel_bp
        from pm_crm.reports.routes import reports_bp

        # Import template_filters
        from .modules import custom_template_filters

        # Uncomment to reset database.
        # init_db()

        # Register Blueprints
        app.register_blueprint(error_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(data_bp)
        app.register_blueprint(rel_bp)
        app.register_blueprint(reports_bp)

        return app
