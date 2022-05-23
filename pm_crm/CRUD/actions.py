from flask import session
from flask_login import current_user
from datetime import date
from ..models import (
    Relationship,
    SLACall,
    SLAMeeting,
)


# def clear_flashes():
#     try:
#         session["_flashes"].clear()
#     except KeyError:
#         pass


# def month_values(cm, num_meetings):
#     valid_months = [x for x in range(1, 13)]
#     meetings = [x for x in range(1, num_meetings)]
#     values = set()
#     values.add(cm)

#     values.update(
#         [
#             cm + int(12 / num_meetings) * x
#             for x in meetings
#             if cm + int(12 / num_meetings) * x in valid_months
#         ]
#     )
#     values.update(
#         [
#             cm - int(12 / num_meetings) * x
#             for x in meetings
#             if cm - int(12 / num_meetings) * x in valid_months
#         ]
#     )

#     return values


# def load_slas(query):
#     current_month = date.today().month
#     month_filter = {}
#     sla_options = [1, 2, 3, 4, 6]
#     for option in sla_options:
#         values = month_values(current_month, option)
#         month_filter[option] = values
#     slas = []
#     for q in query:
#         if q.per_year == 12:
#             slas.append(q.id)
#         elif q.per_year == 0:
#             continue
#         else:
#             for k, v in month_filter.items():
#                 if q.per_year == k and q.month in v:
#                     slas.append(q.id)
#     return slas


# def load_meeting_slas(meeting_sla_ids):
#     meeting_slas = SLAMeeting.query.filter(SLAMeeting.id.in_(meeting_sla_ids)).all()
#     return meeting_slas


# def load_call_slas(call_sla_ids):
#     call_slas = SLACall.query.filter(SLACall.id.in_(call_sla_ids)).all()
#     return call_slas


# def load_rels_with_meetings(meeting_slas):
#     meeting_slas = load_slas(meeting_slas)
#     relationships = (
#         Relationship.query.filter_by(portfolio_manager=current_user.id)
#         .filter(Relationship.meeting_sla.in_(meeting_slas))
#         .order_by(Relationship.name)
#         .all()
#     )

#     for rel in relationships:
#         for i in range(len(rel.meetings)):
#             if (
#                 rel.meetings[i].date_updated.year == date.today().year
#                 and rel.meetings[i].date_updated.month == date.today().month
#             ):
#                 relationships.remove(rel)
#     return relationships


# def load_rels_with_calls(call_slas):
#     call_slas = load_slas(call_slas)
#     relationships = (
#         Relationship.query.filter_by(portfolio_manager=current_user.id)
#         .filter(Relationship.call_sla.in_(call_slas))
#         .order_by(Relationship.name)
#         .all()
#     )

#     for rel in relationships:
#         for i in range(len(rel.calls)):
#             if (
#                 rel.calls[i].date_updated.year == date.today().year
#                 and rel.calls[i].date_updated.month == date.today().month
#             ):
#                 relationships.remove(rel)

#     return relationships


# def confirm_valid_month(per_year, month):
#     if per_year == 2 and month > 6:
#         month = 1
#     elif per_year == 3 and month > 4:
#         month = 1
#     elif per_year == 4 and month > 3:
#         month = 1
#     elif per_year == 6 and month > 2:
#         month = 1
#     elif per_year == 12 and month > 1:
#         month = 1
#     return month
