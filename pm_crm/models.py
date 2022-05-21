from flask import flash, redirect, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

ACCESS_TYPE = ["admin", "SFO", "PM", "IA"]

INVESTMENT_RESPONSIBILITY = ["Sole", "Shared"]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id.lower())


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page"""
    flash("You must be logged in to view that page.", "danger")
    return redirect(url_for("auth_bp.login"))


class User(db.Model, UserMixin):
    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    officer_code = db.Column(db.String(3), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    access_id = db.Column(db.Integer, db.ForeignKey("access.id"), nullable=False)
    lma_accounts = db.relationship("LMAAccount", backref="pm", lazy=True)
    sma_accounts = db.relationship("SMAAccount", backref="pm", lazy=True)
    relationships = db.relationship("Relationship", backref="pm", lazy=True)
    account_update = db.relationship("UpdateAccount", backref="user", lazy=True)
    calls = db.relationship("Call", backref="user", lazy=True)
    meetings = db.relationship("Meeting", backref="user", lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=12
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def load_smas(self):
        smas = (
            SMAAccount.query.filter_by(portfolio_manager=self.id, lma_account=None)
            .order_by(SMAAccount.account_name)
            .all()
        )
        if smas:
            return smas

    def load_lmas(self, filter="", rel_data=False):
        if filter != "":
            query = (
                LMAAccount.query.filter_by(portfolio_manager=self.id)
                .filter(LMAAccount.account_name.contains(filter))
                .order_by(LMAAccount.account_name)
            )
            if rel_data:
                query = query.filter_by(relationship_id=None)
            lmas = query.all()
            if len(lmas) == 0:
                flash("No accounts by that filter", "danger")
        if filter == "" or len(lmas) == 0:
            query = LMAAccount.query.filter_by(portfolio_manager=self.id).order_by(
                LMAAccount.account_name
            )
            if rel_data:
                query = query.filter_by(relationship_id=None)
            lmas = query.all()
        if lmas:
            return lmas

    def load_relationships(self, filter="", sort="name"):
        rels = [
            None,
        ]
        if filter != "":
            rels = (
                Relationship.query.filter_by(portfolio_manager=self.id)
                .filter(Relationship.name.contains(filter))
                .order_by(Relationship.name)
                .all()
            )
        if len(rels) == 0:
            flash("No relationships by that name", "danger")
        if filter == "" or len(rels) == 0:
            if sort == "name":
                rels = (
                    Relationship.query.filter_by(portfolio_manager=self.id)
                    .order_by(Relationship.name)
                    .all()
                )
            elif sort == "mv":
                rels = (
                    Relationship.query.filter_by(portfolio_manager=self.id)
                    .order_by(Relationship.market_value.desc())
                    .all()
                )
        if rels:
            return rels

    def load_relationship(self, name):
        relationship = Relationship.query.filter_by(
            portfolio_manager=self.id, name=name
        ).first()
        return relationship

    def __repr__(self):
        return f"User('{self.name}', {self.officer_code})"


class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    accounts = db.relationship("LMAAccount", backref="relationship", lazy=True)
    portfolio_manager = db.Column(
        db.String(5), db.ForeignKey("user.id"), nullable=False
    )
    market_value = db.Column(db.Float, nullable=False, default=0.0)
    call_sla = db.Column(db.Integer, db.ForeignKey("sla_call.id"), default=1)
    meeting_sla = db.Column(db.Integer, db.ForeignKey("sla_meeting.id"), default=1)
    calls = db.relationship("Call", backref="relationship", lazy=True)
    meetings = db.relationship("Meeting", backref="relationship", lazy=True)

    def load_meeting_sla(self):
        return SLAMeeting.query.filter_by(id=self.meeting_sla).first()

    def load_call_sla(self):
        return SLACall.query.filter_by(id=self.call_sla).first()

    def load_meetings(self):
        return (
            Meeting.query.filter_by(relationship_id=self.id)
            .order_by(Meeting.date_updated.desc())
            .all()
        )

    def load_calls(self):
        return (
            Call.query.filter_by(relationship_id=self.id)
            .order_by(Call.date_updated.desc())
            .all()
        )

    def __repr__(self):
        return f"Relationship('{self.name}', {self.market_value})"


class Call(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    relationship_id = db.Column(
        db.Integer, db.ForeignKey("relationship.id"), nullable=False
    )
    who_updated = db.Column(db.String(5), db.ForeignKey("user.id"), nullable=False)
    date_updated = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f""


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    relationship_id = db.Column(
        db.Integer, db.ForeignKey("relationship.id"), nullable=False
    )
    who_updated = db.Column(db.String(5), db.ForeignKey("user.id"), nullable=False)
    date_updated = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f""


cmonths = db.Table(
    "cmonths",
    db.Column(
        "call_month_id", db.Integer, db.ForeignKey("call_month.id"), primary_key=True
    ),
    db.Column(
        "sla_call_id", db.Integer, db.ForeignKey("sla_call.id"), primary_key=True
    ),
)


class SLACall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    per_year = db.Column(db.Integer, nullable=False)
    months = db.relationship(
        "CallMonth",
        secondary=cmonths,
        lazy="subquery",
        backref=db.backref("sla_calls", lazy=True),
    )
    relationship_id = db.relationship("Relationship", backref="sla_call", lazy=True)

    def __repr__(self):
        return f"Per Year: {self.per_year} - Months: {self.months}"


class CallMonth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month_name = db.Column(db.String(9), unique=True, nullable=False)

    def __repr__(self):
        return f"{self.id}"


mmonths = db.Table(
    "mmonths",
    db.Column(
        "meeting_month_id",
        db.Integer,
        db.ForeignKey("meeting_month.id"),
        primary_key=True,
    ),
    db.Column(
        "sla_meeting_id", db.Integer, db.ForeignKey("sla_meeting.id"), primary_key=True
    ),
)


class SLAMeeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    per_year = db.Column(db.Integer, nullable=False)
    months = db.relationship(
        "MeetingMonth",
        secondary=mmonths,
        lazy="subquery",
        backref=db.backref("sla_meetings", lazy=True),
    )
    relationship_id = db.relationship("Relationship", backref="sla_meeting", lazy=True)

    def __repr__(self):
        return f"Per Year: {self.per_year} - Months: {self.months}"


class MeetingMonth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month_name = db.Column(db.String(9), unique=True, nullable=False)

    def __repr__(self):
        return f"Month('{self.month_name}')"


class LMAAccount(db.Model):
    accountnumber = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(30), unique=True, nullable=False)
    trust_advisor = db.Column(
        db.String(3), db.ForeignKey("ta_officer.code"), nullable=False
    )
    portfolio_manager = db.Column(
        db.String(5), db.ForeignKey("user.id"), nullable=False
    )
    market_value = db.Column(db.Float, nullable=False)
    invest_resp = db.Column(db.Integer, db.ForeignKey("inv_resp.id"), nullable=False)
    update_id = db.Column(
        db.Integer, db.ForeignKey("update_account.id"), nullable=False
    )
    sma = db.relationship("SMAAccount", backref="lma", lazy=True)
    relationship_id = db.Column(db.Integer, db.ForeignKey("relationship.id"))

    def __repr__(self):
        return f"LMAAccount('{self.accountnumber}', '{self.account_name}', {self.market_value})"


class SMAAccount(db.Model):
    accountnumber = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(30), unique=True, nullable=False)
    trust_advisor = db.Column(
        db.String(3), db.ForeignKey("ta_officer.code"), nullable=False
    )
    portfolio_manager = db.Column(
        db.String(5), db.ForeignKey("user.id"), nullable=False
    )
    market_value = db.Column(db.Float, nullable=False)
    invest_resp = db.Column(db.Integer, db.ForeignKey("inv_resp.id"), nullable=False)
    update_id = db.Column(
        db.Integer, db.ForeignKey("update_account.id"), nullable=False
    )
    lma_account = db.Column(db.Integer, db.ForeignKey("lma_account.accountnumber"))

    def __repr__(self):
        return f"SMAAccount('{self.accountnumber}', '{self.account_name}', {self.market_value})"


class UpdateAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(5), db.ForeignKey("user.id"), nullable=False)
    update_date = db.Column(db.DateTime, nullable=False)
    lma_accounts = db.relationship("LMAAccount", backref="lma_update", lazy=True)
    sma_accounts = db.relationship("SMAAccount", backref="sma_update", lazy=True)

    def __repr__(self):
        return f""


class InvResp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inv_resp_type = db.Column(db.String(6), unique=True, nullable=False)
    lma_accounts = db.relationship("LMAAccount", backref="invresp", lazy=True)
    sma_accounts = db.relationship("SMAAccount", backref="invresp", lazy=True)

    def __repr__(self):
        return f"InvResp('{self.inv_resp_type}')"


class TAOfficer(db.Model):
    code = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(30), unique=True)
    lma_accounts = db.relationship("LMAAccount", backref="taofficer", lazy=True)
    sma_accounts = db.relationship("SMAAccount", backref="taofficer", lazy=True)

    def __repr__(self):
        return f"TAOfficer('{self.code}', {self.name})"


class Access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_type = db.Column(db.String(5), unique=True, nullable=False)
    users = db.relationship("User", backref="access", lazy=True)

    def __repr__(self):
        return f"Access('{self.access_type}')"


# class Month(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     month_name = db.Column(db.String(9), unique=True, nullable=False)
#     call_sla = db.relationship("SLACall", backref="call_month", lazy=True)
#     meeting_sla = db.relationship("SLAMeeting", backref="meeting_month", lazy=True)

#     def __repr__(self):
#         return f"Month('{self.month_name}')"


def add_access_types():
    for access in ACCESS_TYPE:
        new = Access(access_type=access)
        db.session.add(new)


def add_ir():
    for ir in INVESTMENT_RESPONSIBILITY:
        new = InvResp(inv_resp_type=ir)
        db.session.add(new)


def add_months():
    for month in MONTHS:
        new_call = CallMonth(month_name=month)
        new_meet = MeetingMonth(month_name=month)
        db.session.add(new_call)
        db.session.add(new_meet)


def add_sla():
    for n in range(13):
        new_sla_call = SLACall(per_year=n)
        new_sla_meeting = SLAMeeting(per_year=n)
        db.session.add(new_sla_call)
        db.session.add(new_sla_meeting)


def populate_db():
    add_access_types()
    add_ir()
    add_months()
    add_sla()


# def link_slas():
#     call_sla = SLACall.query.get(1)
#     meeting_sla = SLAMeeting.query.get(1)
#     c_month = CallMonth.query.get(1)
#     m_month = MeetingMonth.query.get(1)
#     print(call_sla.months)
#     if len(call_sla.months) == 0:
#         call_sla.months.append(c_month)
#     if len(meeting_sla.months) == 0:
#         meeting_sla.months.append(m_month)
