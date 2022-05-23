from datetime import date
from flask_login import current_user
from pm_crm.models import (
    Relationship,
    SLACall,
    cmonths,
    SLAMeeting,
    mmonths,
)


def load_calls(late=False):
    if late == True:
        month = date.today().replace(month=(date.today().month - 1))
        calls = (
            Relationship.query.filter_by(portfolio_manager=current_user.id)
            .join(SLACall)
            .filter(SLACall.per_year != 12)
            .join(cmonths)
            .filter(cmonths.c.call_month_id == month.month)
            .all()
        )
        for call in list(calls):
            if len(call.calls) != 0:
                if max([call.date_updated for call in call.calls]) >= month.replace(
                    day=1
                ):
                    calls.remove(call)
    else:
        month = date.today()
        calls = (
            Relationship.query.filter_by(portfolio_manager=current_user.id)
            .join(SLACall)
            .join(cmonths)
            .filter(cmonths.c.call_month_id == month.month)
            .all()
        )
        for call in list(calls):
            if len(call.calls) != 0:
                if max([call.date_updated for call in call.calls]) >= month.replace(
                    day=1
                ):
                    calls.remove(call)
    return calls


def load_meetings(late=False):
    if late == True:
        month = date.today().replace(month=(date.today().month - 1))
        meetings = (
            Relationship.query.filter_by(portfolio_manager=current_user.id)
            .join(SLAMeeting)
            .filter(SLAMeeting.per_year != 12)
            .join(mmonths)
            .filter(mmonths.c.meeting_month_id == month.month)
            .all()
        )
        for meeting in list(meetings):
            if len(meeting.meetings) != 0:
                if max(
                    [meeting.date_updated for meeting in meeting.meetings]
                ) >= month.replace(day=1):
                    meetings.remove(meeting)
    else:
        month = date.today()
        meetings = (
            Relationship.query.filter_by(portfolio_manager=current_user.id)
            .join(SLAMeeting)
            .join(mmonths)
            .filter(mmonths.c.meeting_month_id == month.month)
            .all()
        )
        for meeting in list(meetings):
            if len(meeting.meetings) != 0:
                if max(
                    [meeting.date_updated for meeting in meeting.meetings]
                ) >= month.replace(day=1):
                    meetings.remove(meeting)
    return meetings
