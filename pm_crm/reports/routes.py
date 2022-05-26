from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

# Blueprint Configuration
reports_bp = Blueprint(
    "reports_bp", __name__, template_folder="templates", static_folder="static"
)


@reports_bp.route("/reports")
@login_required
def reports():
    return render_template("reports.html")
