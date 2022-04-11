from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required
from werkzeug.exceptions import BadRequestKeyError
from pm_crm.CRUD import actions, create


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

    if relationships:
        m_slas = {relationship.meeting_sla for relationship in relationships}
        c_slas = {relationship.call_sla for relationship in relationships}
        meeting_slas = actions.load_meeting_slas(m_slas)
        call_slas = actions.load_call_slas(c_slas)
        meet_peryear = {
            meeting_sla.id: meeting_sla.per_year for meeting_sla in meeting_slas
        }
        call_peryear = {call_sla.id: call_sla.per_year for call_sla in call_slas}
        rels_meetings = actions.load_rels_with_meetings(meeting_slas)
        rels_calls = actions.load_rels_with_calls(call_slas)

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
                    meetings = request.form.getlist("meeting")
                    calls = request.form.getlist("call")
                    if meetings:
                        create.new_meeting(meetings)
                    if calls:
                        create.new_call(calls)
        except BadRequestKeyError:
            pass

        return render_template(
            "main.html",
            relationships=relationships,
            meet_peryear=meet_peryear,
            call_peryear=call_peryear,
            rels_meetings=rels_meetings,
            rels_calls=rels_calls,
        )
    return render_template(
        "main.html",
        relationships=relationships,
    )
