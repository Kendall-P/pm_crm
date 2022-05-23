from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError
from pm_crm.models import Relationship, SLACall, cmonths, Call
from pm_crm.utils import clear_flashes
from pm_crm.main.CRUD import actions
from datetime import date, datetime, timedelta
from sqlalchemy import not_, and_


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

        # m_slas = {relationship.meeting_sla for relationship in relationships}
        # c_slas = {relationship.call_sla for relationship in relationships}
        # meeting_slas = actions.load_meeting_slas(m_slas)
        # call_slas = actions.load_call_slas(c_slas)
        # meet_peryear = {
        #     meeting_sla.id: meeting_sla.per_year for meeting_sla in meeting_slas
        # }
        # call_peryear = {call_sla.id: call_sla.per_year for call_sla in call_slas}

        # test = CallMonth.query.get(5)
        # print(test.sla_calls)

        # rels_meetings = actions.load_rels_with_meetings(meeting_slas)
        # rels_calls = actions.load_rels_with_calls(call_slas)

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
                    # if meetings:
                    #     create.new_meeting(meetings)
                    # if calls:
                    #     create.new_call(calls)
        except BadRequestKeyError:
            pass

        return render_template(
            "main.html",
            relationships=relationships,
            late_calls=late_calls,
            current_calls=current_calls,
            late_meetings=late_meetings,
            current_meetings=current_meetings,
            # meet_peryear=meet_peryear,
            # call_peryear=call_peryear,
            # rels_meetings=rels_meetings,
            # rels_calls=rels_calls,
        )
    return render_template(
        "main.html",
        relationships=relationships,
    )
