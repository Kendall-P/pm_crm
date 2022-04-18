from flask_login import current_user
from pm_crm.models import db, Relationship, LMAAccount


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
