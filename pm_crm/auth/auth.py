from flask import Blueprint, render_template, redirect, url_for, flash
from ..forms import LoginForm, RegistrationForm
from pm_crm.CRUD import actions, create

auth_bp = Blueprint(
    "auth_bp", __name__, template_folder="templates", static_folder="static"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = actions.login(form.user_id.data, form.password.data)
        return redirect(url_for(user))

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        create_user = create.new_user(form)
        return redirect(url_for(create_user))

    return render_template("register.html", form=form)
