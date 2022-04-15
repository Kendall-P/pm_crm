from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, current_user
from pm_crm.models import db
from pm_crm.auth.forms import LoginForm, RegistrationForm
from pm_crm.auth.CRUD import actions, create, update

auth_bp = Blueprint(
    "auth_bp", __name__, template_folder="templates", static_folder="static"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = actions.login(form.user_id.data, form.password.data)
        if user:
            if current_user.attempts > 0:
                update.clear_attempts(user)
                db.session.commit()
            next_page = request.args.get("next")
            return (
                redirect(next_page) if next_page else redirect(url_for("main_bp.main"))
            )
        else:
            flash("Incorrect password.", "danger")
            db.session.commit()
            return redirect(url_for("auth_bp.login"))

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        create_user = create.new_user(form)
        if create_user == "main_bp.home":
            db.session.commit()
        return redirect(url_for(create_user))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main_bp.home"))
