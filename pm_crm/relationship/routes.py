from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError
from sqlalchemy import func
from pm_crm import db
from pm_crm.forms import NewRelationshipForm
from pm_crm.utils import clear_flashes
from pm_crm.relationship.CRUD import actions, create, update

# Blueprint Configuration
rel_bp = Blueprint(
    "rel_bp", __name__, template_folder="templates", static_folder="static"
)


@rel_bp.route("/relationship/<name>", methods=["GET", "POST"])
@login_required
def relationship(name):
    rename_form = NewRelationshipForm()
    rel = current_user.load_relationship(name)
    meeting_months = [month.id for month in rel.sla_meeting.months]
    call_months = [month.id for month in rel.sla_call.months]
    months = actions.load_months()
    calls = rel.load_calls()
    meetings = rel.load_meetings()

    try:
        if request.method == "POST":
            clear_flashes()
            if request.form["action"] == "update_sla":
                m_year = int(request.form.get("meeting_year"))
                m_months = [int(x) for x in request.form.getlist("meeting_month")]
                c_year = int(request.form.get("call_year") or 0)
                c_months = [int(x) for x in request.form.getlist("call_month")]

                # Check if form POST of meetings per year is different than the current relationship meetings per year
                if rel.sla_meeting.per_year != m_year:
                    actions.change_meeting_sla(rel, m_year)
                    db.session.commit()
                elif meeting_months != m_months:
                    if len(m_months) != rel.sla_meeting.per_year:
                        flash(
                            "Number of meeting months selected does not match meetings per year.",
                            "danger",
                        )
                    else:
                        new_sla_meeting = actions.get_meeting_sla(
                            rel.sla_meeting.per_year, m_months
                        )
                        if new_sla_meeting is None:
                            create.new_sla_meeting(rel.sla_meeting.per_year, m_months)
                            db.session.commit()
                            new_sla_meeting = actions.get_meeting_sla(
                                rel.sla_meeting.per_year, m_months
                            )
                        update.update_meeting_sla(rel, new_sla_meeting)
                        db.session.commit()

                # Check if form POST of calls per year is different than the current relationship calls per year
                if rel.sla_call.per_year != c_year:
                    actions.change_call_sla(rel, c_year)
                    db.session.commit()
                elif call_months != c_months:
                    if len(c_months) != rel.sla_call.per_year:
                        flash(
                            "Number of call months selected does not match calls per year.",
                            "danger",
                        )
                    else:
                        new_sla_call = actions.get_call_sla(
                            rel.sla_call.per_year, c_months
                        )
                        if new_sla_call is None:
                            create.new_sla_call(rel.sla_call.per_year, c_months)
                            db.session.commit()
                            new_sla_call = actions.get_call_sla(
                                rel.sla_call.per_year, c_months
                            )
                        update.update_call_sla(rel, new_sla_call)
                        db.session.commit()

            return redirect(url_for("rel_bp.relationship", name=rel.name))

    except BadRequestKeyError:
        if rename_form.validate_on_submit():
            update.update_relationship_name(rel, rename_form.name.data.title())
            db.session.commit()
        return redirect(url_for("rel_bp.relationship", name=rel.name))

    return render_template(
        "relationship.html",
        rename_form=rename_form,
        rel=rel,
        meeting_months=meeting_months,
        call_months=call_months,
        months=months,
        meetings=meetings,
        calls=calls,
    )
