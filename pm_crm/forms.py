from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from flask_wtf.file import FileField, FileRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange
from .models import Access, Month


def access_type_choices():
    return Access.query


def month_choices():
    return Month.query


class RegistrationForm(FlaskForm):
    user_id = StringField("UserID", validators=[DataRequired(), Length(min=4, max=5)])
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=30)])
    officer_code = StringField(
        "Officer Code", validators=[DataRequired(), Length(min=3, max=3)]
    )
    access_type = QuerySelectField(
        "Access",
        validators=[DataRequired()],
        query_factory=access_type_choices,
        get_label=("access_type"),
        default=lambda: Access.query.filter_by(access_type="PM").first(),
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Create")


class LoginForm(FlaskForm):
    user_id = StringField(
        "UserID",
        validators=[DataRequired(), Length(min=4, max=5, message="Invalid UserID")],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class FileUploadForm(FlaskForm):
    file = FileField(
        "File", validators=[FileRequired(message="You must choose a file.")]
    )
    submit = SubmitField("Upload")


class AccountFilterForm(FlaskForm):
    account_name = StringField("Filter Name", validators=[Length(min=3)])


class RelationshipFilterForm(FlaskForm):
    relationship_name = StringField("Filter Name", validators=[Length(min=3)])


class NewRelationshipForm(FlaskForm):
    name = StringField("Relationship Name", validators=[DataRequired(), Length(min=3)])
    submit = SubmitField("Create")


# class UpdateRelationshipSLA(FlaskForm):
#     meetings_per_year = IntegerField(
#         "Meetings Per Year", validators=[DataRequired(), NumberRange(min=0, max=12)]
#     )
#     first_meeting_month = QuerySelectField(
#         "First Meeting Month",
#         validators=[DataRequired()],
#         query_factory=month_choices,
#         get_label=("month_name"),
#     )
#     calls_per_year = IntegerField(
#         "Calls Per Year", validators=[DataRequired(), NumberRange(min=0, max=12)]
#     )
#     first_call_month = QuerySelectField(
#         "First Call Month",
#         validators=[DataRequired()],
#         query_factory=month_choices,
#         get_label=("month_name"),
#     )
#     submit = SubmitField("Update")
