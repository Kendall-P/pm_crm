from flask import flash, request
from flask_login import login_user
from pm_crm.models import db, User
from pm_crm.auth.CRUD.update import clear_attempts, pwd_attempt_increase


def login(user_id, password):
    user = User.query.filter_by(id=user_id.lower()).first()
    if user == None:
        flash("Failed login.", "danger")
        return "auth_bp.login"
    if user.attempts > 4:
        flash("Account locked.", "danger")
        return "auth_bp.login"
    if user and user.check_password(password):
        login_user(user)
        clear_attempts(user)
        next_page = request.args.get("next")
        return next_page or "main_bp.main"
    else:
        incorrect_password = pwd_attempt_increase(user)
        flash(incorrect_password, "danger")
        return "auth_bp.login"
