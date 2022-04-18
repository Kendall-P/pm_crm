from pm_crm.models import Relationship


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
