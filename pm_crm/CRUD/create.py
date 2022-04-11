from flask_login import current_user
from datetime import datetime
from pm_crm.models import (
    db,
    TAOfficer,
    UpdateAccount,
    LMAAccount,
    Relationship,
    SLAMeeting,
    SLACall,
    Meeting,
    Call,
)


def new_ta(ta):
    new_ta = TAOfficer(code=ta)
    db.session.add(new_ta)


def new_update_account_entry(user_id, file_date):
    new_account_update = UpdateAccount(user_id=user_id, update_date=file_date)
    db.session.add(new_account_update)
    db.session.commit()


def new_lma_from_sma(sma):
    new_lma = LMAAccount(
        accountnumber=sma.accountnumber,
        account_name=sma.account_name,
        trust_advisor=sma.trust_advisor,
        portfolio_manager=sma.portfolio_manager,
        market_value=sma.market_value,
        invest_resp=sma.invest_resp,
        update_id=sma.update_id,
    )
    db.session.add(new_lma)


def new_relationship(name):
    new_rel = Relationship(name=name.title(), portfolio_manager=current_user.id)
    db.session.add(new_rel)
    db.session.commit()


def new_meeting_sla(year, month):
    new_m_sla = SLAMeeting(per_year=year, month=month)
    db.session.add(new_m_sla)
    db.session.commit()
    return new_m_sla


def new_call_sla(year, month):
    new_c_sla = SLACall(per_year=year, month=month)
    db.session.add(new_c_sla)
    db.session.commit()
    return new_c_sla


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
