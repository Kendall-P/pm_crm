from flask import flash
from pm_crm.models import db, User


def new_user(form):
    try:
        new_user = User(
            id=form.user_id.data.lower(),
            name=form.name.data.title(),
            officer_code=form.officer_code.data.upper(),
            access_id=form.access_type.data.id,
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        return "main_bp.home"
    except:
        flash("User not added to DB.  Something went wrong.", "danger")
        return "auth_bp.register"
