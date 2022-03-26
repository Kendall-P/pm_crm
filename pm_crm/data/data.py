from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user


# Blueprint Configuration
data_bp = Blueprint(
    "data_bp", __name__, template_folder="templates", static_folder="static"
)


@data_bp.route("/update", methods=["GET", "POST"])
@login_required
def update_data():
    return render_template("update.html")
