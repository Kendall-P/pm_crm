from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError
from pm_crm.CRUD import actions, update

# Blueprint Configuration
rel_bp = Blueprint(
    "rel_bp", __name__, template_folder="templates", static_folder="static"
)


@rel_bp.route("/relationship/<name>", methods=["GET", "POST"])
@login_required
def relationship(name):
    # form = UpdateRelationshipSLA()
    rel = actions.load_relationship(name)
    meeting_sla = actions.load_meeting_sla(rel.meeting_sla)
    call_sla = actions.load_call_sla(rel.call_sla)
    months = actions.load_months()

    try:
        if request.method == "POST":
            actions.clear_flashes()
            if request.form["action"] == "update_sla":
                if (meeting_sla.per_year != request.form.get("meeting_year")) or (
                    meeting_sla.per_month != request.form.get("meeting_month")
                ):
                    # m_year = request.form.get("meeting_year")
                    # m_month = request.form.get("meeting_month")
                    # update.update_meeting_sla(rel, m_year, m_month)
                    print(
                        f'Form:  Meeting/yr: {request.form.get("meeting_year")} Meeting Month: {request.form.get("meeting_month")}'
                    )

                if (call_sla.per_year != request.form.get("call_year")) or (
                    call_sla.per_month != request.form.get("call_month")
                ):
                    #     c_year = request.form.get("call_year")
                    #     c_month = request.form.get("call_month")
                    #     update.update_call_sla(rel, c_year, c_month)
                    print(
                        f'Form:  Call/yr: {request.form.get("call_year")} Call Month: {request.form.get("call_month")}'
                    )
                return redirect(url_for("rel_bp.relationship", name))

    except:
        pass

    # if form.validate_on_submit():
    #     print("Button worked")
    #     print(f"{rel.meeting_sla.per_year} {form.meetings_per_year.data}")
    #     if rel.meeting_sla.per_year != form.meetings_per_year.data:
    #         pass
    #     if rel.meeting_sla.month != form.first_meeting_month.data:
    #         pass
    #     if rel.call_sla.per_year != form.calls_per_year.data:
    #         pass
    #     if rel.call_sla.month != form.first_call_month.data:
    #         pass

    return render_template(
        "relationship.html",
        rel=rel,
        meeting_sla=meeting_sla,
        call_sla=call_sla,
        months=months,
    )
