from flask_login import current_user
from pm_crm.models import db, Relationship


def new_relationship(name):
    new_rel = Relationship(name=name.title(), portfolio_manager=current_user.id)
    db.session.add(new_rel)
