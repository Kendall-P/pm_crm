from flask_login import current_user
from pm_crm.models import db, Relationship, LMAAccount, TAOfficer, UpdateAccount


def new_relationship(name):
    new_rel = Relationship(name=name.title(), portfolio_manager=current_user.id)
    db.session.add(new_rel)


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


def new_ta(ta):
    new_ta = TAOfficer(code=ta)
    db.session.add(new_ta)


def new_update_account_entry(user_id, file_date):
    new_account_update = UpdateAccount(user_id=user_id, update_date=file_date)
    db.session.add(new_account_update)
