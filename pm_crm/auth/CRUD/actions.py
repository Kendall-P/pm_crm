from flask import flash, request
from flask_login import login_user
from pm_crm.models import db, User
from pm_crm.auth.CRUD.update import clear_attempts, pwd_attempt_increase


def login(user_id, password):
    user = User.query.filter_by(id=user_id.lower()).first()
    if user.check_password(password):
        login_user(user)
        return user
    else:
        pwd_attempt_increase(user)
