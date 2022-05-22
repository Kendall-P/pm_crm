from flask_login import current_user
from datetime import datetime
from pm_crm.models import (
    db,
    SLAMeeting,
    SLACall,
    Meeting,
    Call,
)


# def new_meeting_sla(year, month):
#     new_m_sla = SLAMeeting(per_year=year, month=month)
#     db.session.add(new_m_sla)
#     db.session.commit()
#     return new_m_sla


# def new_call_sla(year, month):
#     new_c_sla = SLACall(per_year=year, month=month)
#     db.session.add(new_c_sla)
#     db.session.commit()
#     return new_c_sla


def new_meeting(rel_ids):
    for rel_id in rel_ids:
        new_meet = Meeting(
            relationship_id=rel_id,
            who_updated=current_user.id,
            date_updated=datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
        )
        db.session.add(new_meet)
    db.session.commit()


def new_call(rel_ids):
    for rel_id in rel_ids:
        new_call = Call(
            relationship_id=rel_id,
            who_updated=current_user.id,
            date_updated=datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
        )
        db.session.add(new_call)
    db.session.commit()
