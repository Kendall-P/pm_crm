from pm_crm.models import db, SLACall, CallMonth, SLAMeeting, MeetingMonth


def new_sla_call(per_year, c_months):
    new_call_sla = SLACall(per_year=per_year)
    db.session.add(new_call_sla)
    for month in c_months:
        c_month = CallMonth.query.get(month)
        new_call_sla.months.append(c_month)


def new_sla_meeting(per_year, m_months):
    new_meeting_sla = SLAMeeting(per_year=per_year)
    db.session.add(new_meeting_sla)
    for month in m_months:
        m_month = MeetingMonth.query.get(month)
        new_meeting_sla.months.append(m_month)
