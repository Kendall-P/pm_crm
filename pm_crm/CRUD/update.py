from flask import flash
from pm_crm.models import (
    db,
    SLAMeeting,
    SLACall,
)
from . import create


def update_meeting_sla(rel, year, month):
    m_sla = SLAMeeting.query.filter_by(per_year=year, month=month).first()
    if m_sla is None:
        new_m_sla = create.new_meeting_sla(year, month)
        rel.meeting_sla = new_m_sla.id
    else:
        rel.meeting_sla = m_sla.id
    db.session.commit()
    flash("Meeting SLA updated", "success")


def update_call_sla(rel, year, month):
    c_sla = SLACall.query.filter_by(per_year=year, month=month).first()
    if c_sla is None:
        new_c_sla = create.new_call_sla(year, month)
        rel.call_sla = new_c_sla.id
    else:
        rel.call_sla = c_sla.id
    db.session.commit()
    flash("Call SLA updated", "success")


def update_relationship_name(rel, name):
    rel.name = name
    db.session.commit()
