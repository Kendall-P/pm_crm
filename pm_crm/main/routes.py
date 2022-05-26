from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError
from pm_crm.utils import clear_flashes
from pm_crm.models import db
from pm_crm.main.CRUD import actions, create


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
        relationships = current_user.load_relationships(
            filter="", sort=session["rel_sort"]
        )
    else:
        relationships = current_user.load_relationships(filter="", sort="mv")

    if relationships:

        late_calls = actions.load_calls(late=True)
        current_calls = actions.load_calls()
        late_meetings = actions.load_meetings(late=True)
        current_meetings = actions.load_meetings()

        try:
            if request.method == "POST":
                clear_flashes()
                if request.form["action"] == "sort_name":
                    session["rel_sort"] = "name"
                    return redirect(url_for("main_bp.main"))
                elif request.form["action"] == "sort_mv":
                    session["rel_sort"] = "mv"
                    return redirect(url_for("main_bp.main"))
                elif request.form["action"] == "update":
                    meetings = request.form.getlist("meeting")
                    calls = request.form.getlist("call")
                    if meetings:
                        create.new_meeting(meetings)
                    if calls:
                        create.new_call(calls)
                    db.session.commit()
                return redirect(url_for("main_bp.main"))
        except BadRequestKeyError:
            pass

        return render_template(
            "main.html",
            relationships=relationships,
            late_calls=late_calls,
            current_calls=current_calls,
            late_meetings=late_meetings,
            current_meetings=current_meetings,
        )
    return render_template(
        "main.html",
        relationships=relationships,
    )
