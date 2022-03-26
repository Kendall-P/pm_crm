from flask import flash
from flask_login import current_user
from pm_crm.models import db, User, TAOfficer, UpdateAccount, LMAAccount, Relationship


def new_user(form):
    if User.query.filter_by(id=form.user_id.data).first():
        flash("User already exists.", "danger")
        return "auth_bp.register"
    try:
        new_user = User(
            id=form.user_id.data.lower(),
            name=form.name.data.title(),
            officer_code=form.officer_code.data.upper(),
            access_id=form.access_type.data.id,
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return "main_bp.home"
    except:
        flash("User not added to DB.  Something went wrong.", "danger")
        return "auth_bp.register"
