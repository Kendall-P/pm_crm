from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from pm_crm.models import Access, User


def access_type_choices():
    return Access.query


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

    def validate_user_id(self, user_id):
        user = User.query.filter_by(id=user_id.data.lower()).first()
        if user:
            raise ValidationError("User already exists.")


class LoginForm(FlaskForm):
    user_id = StringField(
        "UserID",
        validators=[DataRequired(), Length(min=4, max=5, message="Invalid UserID")],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

    def validate_user_id(self, user_id):
        user = User.query.filter_by(id=user_id.data.lower()).first()
        if user == None:
            raise ValidationError("User does not exist.")
        if user.attempts > 4:
            raise ValidationError("Account locked.")
