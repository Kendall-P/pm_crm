from flask_login import current_user
from datetime import date
from pm_crm.models import db, Meeting, Call


def new_meeting(rel_ids):
    for rel_id in rel_ids:
        new_meet = Meeting(
            relationship_id=rel_id,
            who_updated=current_user.id,
            date_updated=date.today(),
        )
        db.session.add(new_meet)


def new_call(rel_ids):
    for rel_id in rel_ids:
        new_call = Call(
            relationship_id=rel_id,
            who_updated=current_user.id,
            date_updated=date.today(),
        )
        db.session.add(new_call)
