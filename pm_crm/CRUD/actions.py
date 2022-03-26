from flask import flash, request, session
from flask_login import login_user, current_user

from ..models import (
    Month,
    User,
    InvResp,
    TAOfficer,
    UpdateAccount,
    SMAAccount,
    LMAAccount,
    Relationship,
    SLACall,
    SLAMeeting,
)

from .update import (
    pwd_attempt_increase,
    clear_attempts,
)


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


def clear_flashes():
    try:
        session["_flashes"].clear()
    except KeyError:
        pass


def load_relationships(filter="", sort="name"):
    if filter != "":
        relationships = (
            Relationship.query.filter_by(portfolio_manager=current_user.id)
            .filter(Relationship.name.contains(filter))
            .order_by(Relationship.name)
            .all()
        )
        if len(relationships) == 0:
            flash("No accounts by that filter", "danger")
    if filter == "" or len(relationships) == 0:
        if sort == "name":
            relationships = (
                Relationship.query.filter_by(portfolio_manager=current_user.id)
                .order_by(Relationship.name)
                .all()
            )
        elif sort == "mv":
            relationships = (
                Relationship.query.filter_by(portfolio_manager=current_user.id)
                .order_by(Relationship.market_value.desc())
                .all()
            )
    if relationships:
        return relationships
    else:
        flash("Relationships load did not work", "danger")
