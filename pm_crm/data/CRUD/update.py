from pm_crm.models import db, Relationship, LMAAccount, SMAAccount, UpdateAccount


def update_sma_link(sma, lma):
    sma.lma_account = lma


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
    return data_frame


def data_frame_to_sql(account_type, data_frame):
    data_frame.to_sql(
        name=f"{account_type}_account",
        con=db.engine,
        index_label="accountnumber",
        if_exists="append",
    )


def update_rel_link(lma, rel_id):
    lma.relationship_id = rel_id
