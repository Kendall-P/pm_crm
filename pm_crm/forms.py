from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Length

# from .models import Month


# def month_choices():
#     return Month.query


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
