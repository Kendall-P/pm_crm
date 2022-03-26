from pm_crm.models import db, SMAAccount, LMAAccount, UpdateAccount, Relationship


def pwd_attempt_increase(user):
    user.attempts += 1
    db.session.commit()
    return "Incorrect password."


def clear_attempts(user):
    if user.attempts > 0:
        user.attempts = 0
        db.session.commit()
