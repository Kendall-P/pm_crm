from flask import flash, session
from flask_login import current_user
from datetime import date, datetime
from os import remove
import pandas as pd
from .. import datafiles, db
from ..models import (
    Month,
    User,
    InvResp,
    TAOfficer,
    UpdateAccount,
    SMAAccount,
    LMAAccount,
    Relationship,
    SLACall,
    SLAMeeting,
    Meeting,
    Call,
)
from .update import (
    database_update,
    update_sma_link,
    update_rel_link,
    update_relationship_mv,
)
from .create import new_ta, new_update_account_entry, new_lma_from_sma
from .delete import delete_sma


def clear_flashes():
    try:
        session["_flashes"].clear()
    except KeyError:
        pass


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
    else:
        # flash("Relationships load did not work", "danger")
        pass


def load_months():
    months = Month.query.all()
    return months


def load_relationship(name):
    relationship = Relationship.query.filter_by(
        portfolio_manager=current_user.id, name=name
    ).first()
    return relationship


def load_meeting_sla(rel_id):
    meeting_sla = SLAMeeting.query.filter_by(id=rel_id).first()
    return meeting_sla


def load_call_sla(rel_id):
    call_sla = SLACall.query.filter_by(id=rel_id).first()
    return call_sla


def load_smas():
    smas = (
        SMAAccount.query.filter_by(portfolio_manager=current_user.id, lma_account=None)
        .order_by(SMAAccount.account_name)
        .all()
    )
    if smas:
        return smas
    else:
        # flash("SMA load did not work", "danger")
        pass


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
    else:
        # flash("LMA load did not work", "danger")
        pass


def month_values(cm, num_meetings):
    valid_months = [x for x in range(1, 13)]
    meetings = [x for x in range(1, num_meetings)]
    values = set()
    values.add(cm)

    values.update(
        [
            cm + int(12 / num_meetings) * x
            for x in meetings
            if cm + int(12 / num_meetings) * x in valid_months
        ]
    )
    values.update(
        [
            cm - int(12 / num_meetings) * x
            for x in meetings
            if cm - int(12 / num_meetings) * x in valid_months
        ]
    )

    return values


def load_slas(query):
    current_month = date.today().month
    month_filter = {}
    sla_options = [1, 2, 3, 4, 6]
    for option in sla_options:
        values = month_values(current_month, option)
        month_filter[option] = values
    slas = []
    for q in query:
        if q.per_year == 12:
            slas.append(q.id)
        elif q.per_year == 0:
            continue
        else:
            for k, v in month_filter.items():
                if q.per_year == k and q.month in v:
                    slas.append(q.id)
    return slas


def load_meeting_slas(meeting_sla_ids):
    meeting_slas = SLAMeeting.query.filter(SLAMeeting.id.in_(meeting_sla_ids)).all()
    return meeting_slas


def load_call_slas(call_sla_ids):
    call_slas = SLACall.query.filter(SLACall.id.in_(call_sla_ids)).all()
    return call_slas


def load_rels_with_meetings(meeting_slas):
    meeting_slas = load_slas(meeting_slas)
    relationships = (
        Relationship.query.filter_by(portfolio_manager=current_user.id)
        .filter(Relationship.meeting_sla.in_(meeting_slas))
        .order_by(Relationship.name)
        .all()
    )

    for rel in relationships:
        for i in range(len(rel.meetings)):
            if (
                rel.meetings[i].date_updated.year == date.today().year
                and rel.meetings[i].date_updated.month == date.today().month
            ):
                relationships.remove(rel)
    return relationships


def load_rels_with_calls(call_slas):
    call_slas = load_slas(call_slas)
    relationships = (
        Relationship.query.filter_by(portfolio_manager=current_user.id)
        .filter(Relationship.call_sla.in_(call_slas))
        .order_by(Relationship.name)
        .all()
    )

    for rel in relationships:
        for i in range(len(rel.calls)):
            if (
                rel.calls[i].date_updated.year == date.today().year
                and rel.calls[i].date_updated.month == date.today().month
            ):
                relationships.remove(rel)

    return relationships


def load_meetings(rel_id):
    meetings = (
        Meeting.query.filter_by(relationship_id=rel_id)
        .order_by(Meeting.date_updated.desc())
        .all()
    )
    return meetings


def load_calls(rel_id):
    calls = (
        Call.query.filter_by(relationship_id=rel_id)
        .order_by(Call.date_updated.desc())
        .all()
    )
    return calls


def convert_to_lma(selected_smas):
    # smas = SMAAccount.query.filter(SMAAccount.accountnumber.in_(selected_smas)).all()
    for sma in selected_smas:
        current_sma = SMAAccount.query.filter_by(accountnumber=sma).first()
        new_lma_from_sma(current_sma)
        delete_sma(current_sma)
    db.session.commit()
    flash("SMA converted to LMA", "success")


def link_to_lma(selected_smas, selected_lma):
    for sma in selected_smas:
        current_sma = SMAAccount.query.filter_by(accountnumber=sma).first()
        update_sma_link(current_sma, selected_lma)
    db.session.commit()
    lma = LMAAccount.query.filter_by(accountnumber=selected_lma).first()
    if lma.relationship_id != None:
        update_relationship_mv(lma.relationship_id)
    db.session.commit()
    flash("SMA linked to LMA", "success")


def link_to_rel(selected_lmas, selected_rel):
    for lma in selected_lmas:
        current_lma = LMAAccount.query.filter_by(accountnumber=lma).first()
        update_rel_link(current_lma, selected_rel)
    db.session.commit()
    update_relationship_mv(selected_rel)
    db.session.commit()
    flash("Account linked to Relationship", "success")


def confirm_valid_month(per_year, month):
    if per_year == 2 and month > 6:
        month = 1
    elif per_year == 3 and month > 4:
        month = 1
    elif per_year == 4 and month > 3:
        month = 1
    elif per_year == 6 and month > 2:
        month = 1
    elif per_year == 12 and month > 1:
        month = 1
    return month


def file_upload_delete(filename):
    # DELETE FILE
    remove(datafiles.path(filename))


def prepare_file(file):
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
        return "data_bp.update_data"

    df.columns = [x.lower().replace(" ", "_") for x in df.columns]

    if all(x in df.loc[0, "account_universe"] for x in ["PA", "PM"]):
        pm_userid = df.loc[0, "account_universe"].split()[0].lower()
    else:
        flash("Report was not run for LMA and SMA.", "danger")
        return "data_bp.update_data"
    if current_user.id != df.loc[0, "requester"].lower():
        flash("Please rerun report and upload again.", "danger")
        return "data_bp.update_data"

    file_date = datetime.combine(
        datetime.strptime(df.loc[0, "valuation"], "%m/%d/%Y %H:%M").date(),
        datetime.min.time(),
    )

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

    # Check if TA's in TAOfficer Table if not add
    to_commit = False
    for ta in df["trust_advisor"].unique():
        if not TAOfficer.query.filter_by(code=ta).first():
            to_commit = True
            new_ta(ta)
    if to_commit:
        db.session.commit()

    # Create entry in UpdateAccount
    update_account_entry = UpdateAccount.query.filter_by(
        user_id=current_user.id, update_date=file_date
    ).first()
    if not update_account_entry:
        new_update_account_entry(current_user.id, file_date)
        update_account_id = (
            UpdateAccount.query.filter_by(
                user_id=current_user.id, update_date=file_date
            )
            .first()
            .id
        )
    else:
        update_account_id = update_account_entry.id

    # Add update_id column with key from entry created above
    df["update_id"] = update_account_id

    off_code = User.query.filter_by(id=pm_userid).first().officer_code
    filt = df["portfolio_manager"] == off_code

    df_sma = df[~filt].copy()

    # Check if NFP and convert SMA to LMA
    for i in df_sma.index:
        account = LMAAccount.query.filter_by(accountnumber=i).first()
        if account:
            df.loc[i, "portfolio_manager"] = off_code
            df_sma.drop(i, inplace=True)

    database_update("sma", df_sma, pm_userid, file_date, update_account_id)

    filt = df["portfolio_manager"] == off_code
    df_lma = df[filt].copy()
    database_update("lma", df_lma, pm_userid, file_date, update_account_id)

    relationships = Relationship.query.filter_by(
        portfolio_manager=current_user.id
    ).all()
    for relationship in relationships:
        if relationship.accounts:
            update_relationship_mv(relationship.id)
    db.session.commit()

    flash("Database updated.", "success")
