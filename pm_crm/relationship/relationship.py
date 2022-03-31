from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError
from pm_crm.forms import NewRelationshipForm
from pm_crm.CRUD import actions, update

# Blueprint Configuration
rel_bp = Blueprint(
    "rel_bp", __name__, template_folder="templates", static_folder="static"
)


@rel_bp.route("/relationship/<name>", methods=["GET", "POST"])
@login_required
def relationship(name):
    rename_form = NewRelationshipForm()
    rel = actions.load_relationship(name)
    meeting_sla = actions.load_meeting_sla(rel.meeting_sla)
    call_sla = actions.load_call_sla(rel.call_sla)
    months = actions.load_months()
    calls = actions.load_calls(rel.id)
    meetings = actions.load_meetings(rel.id)

    try:
        if request.method == "POST":
            actions.clear_flashes()
            if request.form["action"] == "update_sla":

                m_year = int(request.form.get("meeting_year") or 0)
                m_month = int(request.form.get("meeting_month") or 0)
                c_year = int(request.form.get("call_year") or 0)
                c_month = int(request.form.get("call_month") or 0)

                if m_month == 0:
                    m_month = meeting_sla.month
                if c_month == 0:
                    c_month = call_sla.month

                if (meeting_sla.per_year != m_year) or (meeting_sla.month != m_month):
                    m_month = actions.confirm_valid_month(m_year, m_month)
                    update.update_meeting_sla(rel, m_year, m_month)

                if (call_sla.per_year != c_year) or (call_sla.month != c_month):
                    c_month = actions.confirm_valid_month(c_year, c_month)
                    update.update_call_sla(rel, c_year, c_month)

                meeting_sla = actions.load_meeting_sla(rel.meeting_sla)
                call_sla = actions.load_call_sla(rel.call_sla)
            return redirect(url_for("rel_bp.relationship", name=rel.name))

    except BadRequestKeyError:
        if rename_form.validate_on_submit():
            calls = actions.load_calls()

            update.update_relationship_name(rel, rename_form.name.data.title())
            return redirect(url_for("rel_bp.relationship", name=rel.name))

    return render_template(
        "relationship.html",
        rename_form=rename_form,
        rel=rel,
        meeting_sla=meeting_sla,
        call_sla=call_sla,
        months=months,
        meetings=meetings,
        calls=calls,
    )
