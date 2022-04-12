from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Length


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
