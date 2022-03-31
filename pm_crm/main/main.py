from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required, logout_user, current_user
from werkzeug.exceptions import BadRequestKeyError
from pm_crm.CRUD import actions


# Blueprint Configuration
main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)


@main_bp.route("/", methods=["GET"])
@main_bp.route("/index", methods=["GET"])
def home():
    return render_template("index.html")


@main_bp.route("/main", methods=["GET", "POST"])
@login_required
def main():
    if "rel_sort" in session:
        relationships = actions.load_relationships(filter="", sort=session["rel_sort"])
    else:
        relationships = actions.load_relationships(filter="", sort="mv")

    m_slas = {relationship.meeting_sla for relationship in relationships}
    c_slas = {relationship.call_sla for relationship in relationships}
    rels_meetings = actions.load_meeting_slas(m_slas)
    rels_calls = actions.load_call_slas(c_slas)

    try:
        if request.method == "POST":
            actions.clear_flashes()
            if request.form["action"] == "sort_name":
                session["rel_sort"] = "name"
                return redirect(url_for("main_bp.main"))
            elif request.form["action"] == "sort_mv":
                session["rel_sort"] = "mv"
                return redirect(url_for("main_bp.main"))
            elif request.form["action"] == "update":
                print(request.form.getlist("meeting"))
                print(request.form.getlist("call"))
    except BadRequestKeyError:
        pass

    return render_template(
        "main.html",
        relationships=relationships,
        rels_meetings=rels_meetings,
        rels_calls=rels_calls,
    )


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main_bp.home"))
