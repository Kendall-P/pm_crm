from flask import flash
from flask_login import current_user
from os import remove
from datetime import datetime
import pandas as pd
from pm_crm import datafiles
from pm_crm.models import (
    db,
    SMAAccount,
    LMAAccount,
    Relationship,
    InvResp,
    TAOfficer,
    UpdateAccount,
    User,
)
from .create import new_lma_from_sma, new_ta
from .delete import delete_sma
from .update import (
    update_sma_link,
    update_relationship_mv,
    database_update,
    update_rel_link,
)


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


def link_to_rel(selected_lmas, selected_rel):
    for lma in selected_lmas:
        current_lma = LMAAccount.query.filter_by(accountnumber=lma).first()
        update_rel_link(current_lma, selected_rel)


def file_upload_delete(filename):
    # DELETE FILE
    remove(datafiles.path(filename))


def convert_file_to_df(file):
    cols = [
        "Account Number",
        "Account Name",
        "Officer 1",
        "Officer 2",
        "Market Value",
        "Investment Responsibility",
        "Account Universe",
        "Requester",
        "Valuation",
    ]

    try:
        df = pd.read_csv(
            datafiles.path(file),
            sep="\t",
            usecols=cols,
        )
    except ValueError:
        flash("Invalid IWS report.", "danger")
        return None

    df.columns = [x.lower().replace(" ", "_") for x in df.columns]

    if current_user.id != df.loc[0, "requester"].lower():
        flash("Please rerun report and upload again.", "danger")
        return None
    return df


def get_pm_userid(df):
    if all(x in df.loc[0, "account_universe"] for x in ["PA", "PM"]):
        pm_userid = df.loc[0, "account_universe"].split()[0].lower()
        return pm_userid
    else:
        flash("Report was not run for LMA and SMA.", "danger")
        return None


def get_file_date(df):
    file_date = datetime.combine(
        datetime.strptime(df.loc[0, "valuation"], "%m/%d/%Y %H:%M").date(),
        datetime.min.time(),
    )
    return file_date


def df_cleanup(df):
    # Delete no longer needed columns
    df.drop(columns=["account_universe", "requester", "valuation"], inplace=True)

    # Change Invesment Responsibility to Key value
    query = db.session.query(InvResp.id, InvResp.inv_resp_type).distinct(
        InvResp.inv_resp_type
    )
    IR_DICT = {q.inv_resp_type: q.id for q in query}
    df["investment_responsibility"] = df["investment_responsibility"].apply(
        lambda x: IR_DICT[x]
    )

    # Remove "-" from account number
    df["account_number"] = df["account_number"].apply(lambda x: int(x.replace("-", "")))

    # Change Index to Account Number
    df.set_index("account_number", inplace=True)

    df.rename(
        columns={
            "account_number": "accountnumber",
            "officer_1": "trust_advisor",
            "officer_2": "portfolio_manager",
            "investment_responsibility": "invest_resp",
        },
        inplace=True,
    )
    return df


def check_db_ta(df):
    # Check if TA's in TAOfficer Table if not add
    to_commit = False
    for ta in df["trust_advisor"].unique():
        if not TAOfficer.query.filter_by(code=ta).first():
            to_commit = True
            new_ta(ta)
    if to_commit:
        return True


def get_update_id(file_date):
    # Create entry in UpdateAccount
    update_account_entry = UpdateAccount.query.filter_by(
        user_id=current_user.id, update_date=file_date
    ).first()
    if update_account_entry:
        return update_account_entry.id


def df_add_update_id(df, update_account_id):
    # Add update_id column with key from entry created above
    df["update_id"] = update_account_id
    return df


def get_off_code(pm_userid):
    off_code = User.query.filter_by(id=pm_userid).first().officer_code
    return off_code


def remove_nfp_smas(df, off_code):
    filt = df["portfolio_manager"] == off_code

    df_sma = df[~filt].copy()

    # Check if NFP and convert SMA to LMA
    for i in df_sma.index:
        account = LMAAccount.query.filter_by(accountnumber=i).first()
        if account:
            df.loc[i, "portfolio_manager"] = off_code
    return df


def update_smas(df, off_code, pm_userid, file_date, update_account_id):
    filt = df["portfolio_manager"] == off_code
    df_sma = df[~filt].copy()
    data = database_update("sma", df_sma, pm_userid, file_date, update_account_id)
    return data


def update_lmas(df, off_code, pm_userid, file_date, update_account_id):
    filt = df["portfolio_manager"] == off_code
    df_lma = df[filt].copy()
    data = database_update("lma", df_lma, pm_userid, file_date, update_account_id)
    return data


def update_rel_mv(pm_userid):
    relationships = Relationship.query.filter_by(portfolio_manager=pm_userid).all()
    for relationship in relationships:
        if relationship.accounts:
            update_relationship_mv(relationship.id)
