from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from flask_uploads import UploadNotAllowed
from werkzeug.exceptions import BadRequestKeyError
from pm_crm.models import db
from pm_crm.data.forms import (
    FileUploadForm,
    AccountFilterForm,
    RelationshipFilterForm,
    NewRelationshipForm,
)
from pm_crm.CRUD import actions, create
from .. import datafiles


# Blueprint Configuration
data_bp = Blueprint(
    "data_bp", __name__, template_folder="templates", static_folder="static"
)


@data_bp.route("/update", methods=["GET", "POST"])
@login_required
def update_data():
    smas = actions.load_smas()
    if "lma_filter" in session:
        lmas = actions.load_lmas(filter=session["lma_filter"])
    else:
        lmas = actions.load_lmas(filter="")

    lma_filter_form = AccountFilterForm()
    file_form = FileUploadForm()

    try:
        if request.method == "POST":
            actions.clear_flashes()
            if request.form["action"] == "convert":
                selected_smas = request.form.getlist("sma_account")
                actions.convert_to_lma(selected_smas)
            elif request.form["action"] == "link":
                selected_smas = request.form.getlist("sma_account")
                selected_lma = request.form.get("lma_account")
                actions.link_to_lma(selected_smas, selected_lma)
            elif request.form["action"] == "filter":
                lma_filter_form.validate()
                name = lma_filter_form.account_name.data.upper()
                if name:
                    session["lma_filter"] = name
                else:
                    session["lma_filter"] = ""
            else:
                flash("Button did not work", "danger")
            return redirect(url_for("data_bp.update_data"))
    except BadRequestKeyError:
        if file_form.validate_on_submit():
            try:
                uploaded_file = datafiles.save(file_form.file.data)
            except UploadNotAllowed:
                flash("Not an approved file type.", "danger")
                return redirect(url_for("data_bp.update_data"))
            # DO STUFF TO FILE
            actions.prepare_file(uploaded_file)

            #  Delete uploaded file
            actions.file_upload_delete(uploaded_file)
            return redirect(url_for("data_bp.update_data"))

    return render_template(
        "update.html",
        smas=smas,
        lmas=lmas,
        lma_filter_form=lma_filter_form,
        file_form=file_form,
    )


@data_bp.route("/relationships", methods=["GET", "POST"])
@login_required
def link_accounts():
    if "lma_filter" in session:
        lmas = actions.load_lmas(filter=session["lma_filter"], rel_data=True)
    else:
        lmas = actions.load_lmas(filter="", rel_data=True)
    if "rel_filter" in session:
        relationships = actions.load_relationships(filter=session["rel_filter"])
    else:
        relationships = actions.load_relationships(filter="")

    form = NewRelationshipForm()

    rel_filter_form = RelationshipFilterForm()
    lma_filter_form = AccountFilterForm()

    try:
        if request.method == "POST":
            actions.clear_flashes()
            if request.form["action"] == "filter_lma":
                lma_filter_form.validate()
                name = lma_filter_form.account_name.data.upper()
                if name:
                    session["lma_filter"] = name
                else:
                    session["lma_filter"] = ""
            elif request.form["action"] == "filter_rel":
                rel_filter_form.validate()
                name = rel_filter_form.relationship_name.data.title()
                if name:
                    session["rel_filter"] = name
                else:
                    session["rel_filter"] = ""
            elif request.form["action"] == "link":
                selected_lmas = request.form.getlist("lma_account")
                selected_rel = request.form.get("relationship")
                session["lma_filter"] = ""
                session["rel_filter"] = ""
                actions.link_to_rel(selected_lmas, selected_rel)
            return redirect(url_for("data_bp.link_accounts"))

    except BadRequestKeyError:
        if form.validate_on_submit():
            create.new_relationship(form.name.data)
            db.session.commit()
            return redirect(url_for("data_bp.link_accounts"))

    return render_template(
        "link.html",
        lmas=lmas,
        relationships=relationships,
        form=form,
        rel_filter_form=rel_filter_form,
        lma_filter_form=lma_filter_form,
    )
