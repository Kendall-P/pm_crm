from flask import flash
from pm_crm.models import db, SMAAccount


def delete_sma(sma):
    db.session.delete(sma)
