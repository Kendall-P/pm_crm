from flask import flash
from flask_login import current_user
from pm_crm.models import SMAAccount, LMAAccount, Relationship
from .create import new_lma_from_sma
from .delete import delete_sma
from .update import update_sma_link, update_relationship_mv


def load_smas():
    smas = (
        SMAAccount.query.filter_by(portfolio_manager=current_user.id, lma_account=None)
        .order_by(SMAAccount.account_name)
        .all()
    )
    if smas:
        return smas


def load_lmas(filter="", rel_data=False):
    if filter != "":
        query = (
            LMAAccount.query.filter_by(portfolio_manager=current_user.id)
            .filter(LMAAccount.account_name.contains(filter))
            .order_by(LMAAccount.account_name)
        )
        if rel_data:
            query = query.filter_by(relationship_id=None)
        lmas = query.all()
        if len(lmas) == 0:
            flash("No accounts by that filter", "danger")
    if filter == "" or len(lmas) == 0:
        query = LMAAccount.query.filter_by(portfolio_manager=current_user.id).order_by(
            LMAAccount.account_name
        )
        if rel_data:
            query = query.filter_by(relationship_id=None)
        lmas = query.all()
    if lmas:
        return lmas


def load_relationships(filter="", sort="name"):
    if filter != "":
        relationships = (
            Relationship.query.filter_by(portfolio_manager=current_user.id)
            .filter(Relationship.name.contains(filter))
            .order_by(Relationship.name)
            .all()
        )
        if len(relationships) == 0:
            flash("No relationships by that filter", "danger")
    if filter == "" or len(relationships) == 0:
        if sort == "name":
            relationships = (
                Relationship.query.filter_by(portfolio_manager=current_user.id)
                .order_by(Relationship.name)
                .all()
            )
        elif sort == "mv":
            relationships = (
                Relationship.query.filter_by(portfolio_manager=current_user.id)
                .order_by(Relationship.market_value.desc())
                .all()
            )
    if relationships:
        return relationships


def convert_to_lma(selected_smas):
    # smas = SMAAccount.query.filter(SMAAccount.accountnumber.in_(selected_smas)).all()
    for sma in selected_smas:
        current_sma = SMAAccount.query.filter_by(accountnumber=sma).first()
        new_lma_from_sma(current_sma)
        delete_sma(current_sma)


def link_to_lma(selected_smas, selected_lma):
    for sma in selected_smas:
        current_sma = SMAAccount.query.filter_by(accountnumber=sma).first()
        update_sma_link(current_sma, selected_lma)
    lma = LMAAccount.query.filter_by(accountnumber=selected_lma).first()
    if lma.relationship_id != None:
        update_relationship_mv(lma.relationship_id)
