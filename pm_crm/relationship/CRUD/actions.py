from sqlalchemy import func
from pm_crm.models import CallMonth, SLAMeeting, SLACall, cmonths, mmonths
from .update import update_meeting_sla, update_call_sla


def load_months():
    months = CallMonth.query.all()
    return months


def change_meeting_sla(rel, m_year):
    if m_year == 12:
        meeting_sla = SLAMeeting.query.filter_by(per_year=m_year).first()
    else:
        meeting_sla = (
            SLAMeeting.query.filter_by(per_year=m_year)
            .filter(~SLAMeeting.months.any())
            .first()
        )
    if meeting_sla:
        update_meeting_sla(rel, meeting_sla)


def change_call_sla(rel, c_year):
    if c_year == 12:
        call_sla = SLACall.query.filter_by(per_year=c_year).first()
    else:
        call_sla = (
            SLACall.query.filter_by(per_year=c_year)
            .filter(~SLACall.months.any())
            .first()
        )
    if call_sla:
        update_call_sla(rel, call_sla)


def get_call_sla(per_year, c_months):
    new_sla_call = (
        SLACall.query.filter_by(per_year=per_year)
        .join(cmonths)
        .filter(cmonths.c.call_month_id.in_(c_months))
        .group_by(cmonths.c.sla_call_id)
        .having(func.count(cmonths.c.call_month_id) == len(c_months))
        .first()
    )
    return new_sla_call


def get_meeting_sla(per_year, m_months):
    new_sla_meeting = (
        SLAMeeting.query.filter_by(per_year=per_year)
        .join(mmonths)
        .filter(mmonths.c.meeting_month_id.in_(m_months))
        .group_by(mmonths.c.sla_meeting_id)
        .having(func.count(mmonths.c.meeting_month_id) == len(m_months))
        .first()
    )
    return new_sla_meeting
