from pm_crm.models import db


def delete_sma(sma):
    db.session.delete(sma)
