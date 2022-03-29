from flask import flash
from pm_crm.models import (
    db,
    SMAAccount,
    LMAAccount,
    UpdateAccount,
    Relationship,
    SLAMeeting,
    SLACall,
)
from . import create


def pwd_attempt_increase(user):
    user.attempts += 1
    db.session.commit()
    return "Incorrect password."


def clear_attempts(user):
    if user.attempts > 0:
        user.attempts = 0
        db.session.commit()


def update_sma_link(sma, lma):
    sma.lma_account = lma


def update_rel_link(lma, rel_id):
    lma.relationship_id = rel_id


def update_account(account, slice, pm_userid, update_account_id):
    if account.account_name != slice["account_name"]:
        account.account_name = slice["account_name"]
    if account.trust_advisor != slice["trust_advisor"]:
        account.trust_advisor = slice["trust_advisor"]
    if account.portfolio_manager != pm_userid:
        account.portfolio_manager = pm_userid
    if account.invest_resp != int(slice["invest_resp"]):
        account.invest_resp = int(slice["invest_resp"])
    account.market_value = slice["market_value"]
    account.update_id = update_account_id
    db.session.commit()


def update_relationship_mv(relationship_id):
    relationship = Relationship.query.filter_by(id=relationship_id).first()
    accounts = relationship.accounts
    lmas_value = sum([account.market_value for account in accounts])
    smas_value = 0
    for account in accounts:
        if account.sma:
            for n in range(len(account.sma)):
                smas_value += account.sma[n].market_value
    relationship.market_value = lmas_value + smas_value


def update_meeting_sla(rel, year, month):
    m_sla = SLAMeeting.query.filter_by(per_year=year, month=month).first()
    if m_sla is None:
        new_m_sla = create.new_meeting_sla(year, month)
        rel.meeting_sla = new_m_sla.id
    else:
        rel.meeting_sla = m_sla.id
    db.session.commit()
    flash("Meeting SLA updated", "success")


def update_call_sla(rel, year, month):
    c_sla = SLACall.query.filter_by(per_year=year, month=month).first()
    if c_sla is None:
        new_c_sla = create.new_call_sla(year, month)
        rel.call_sla = new_c_sla.id
    else:
        rel.call_sla = c_sla.id
    db.session.commit()
    flash("Call SLA updated", "success")


def update_relationship_name(rel, name):
    rel.name = name
    db.session.commit()


def database_update(account_type, data_frame, pm_userid, file_date, update_account_id):

    data_frame["portfolio_manager"] = pm_userid
    accounts_to_drop = []

    for i in data_frame.index:
        if account_type == "lma":
            account = LMAAccount.query.filter_by(accountnumber=i).first()
        elif account_type == "sma":
            account = SMAAccount.query.filter_by(accountnumber=i).first()
        if account:

            # TODO - Is there a better search method?
            if (
                UpdateAccount.query.filter_by(id=account.update_id).first().update_date
                < file_date
            ):
                # Update Account table with entry
                update_account(account, data_frame.loc[i], pm_userid, update_account_id)

            # Delete row from df
            accounts_to_drop.append(i)
    data_frame.drop(accounts_to_drop, inplace=True)

    data_frame.to_sql(
        name=f"{account_type}_account",
        con=db.engine,
        index_label="accountnumber",
        if_exists="append",
    )
