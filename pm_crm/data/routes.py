from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from flask_uploads import UploadNotAllowed
from wtforms.validators import ValidationError
from werkzeug.exceptions import BadRequestKeyError
from pm_crm import datafiles, db
from pm_crm.models import Relationship
from pm_crm.utils import clear_flashes
from pm_crm.data.forms import (
    FileUploadForm,
    AccountFilterForm,
    RelationshipFilterForm,
    NewRelationshipForm,
)
from pm_crm.data.CRUD import actions, create, update


# Blueprint Configuration
data_bp = Blueprint(
    "data_bp", __name__, template_folder="templates", static_folder="static"
)


@data_bp.route("/update", methods=["GET", "POST"])
@login_required
def update_data():
    lma_filter_form = AccountFilterForm()
    file_form = FileUploadForm()

    if request.method == "GET":
        smas = current_user.load_smas()
        if "lma_filter" in session:
            lmas = current_user.load_lmas(filter=session["lma_filter"])
        else:
            lmas = current_user.load_lmas(filter="")

    try:
        if request.method == "POST":
            clear_flashes()
            if request.form["action"] == "convert":
                selected_smas = request.form.getlist("sma_account")
                actions.convert_to_lma(selected_smas)
                db.session.commit()
                flash("SMA converted to LMA", "success")
            elif request.form["action"] == "link":
                selected_smas = request.form.getlist("sma_account")
                selected_lma = request.form.get("lma_account")
                if selected_smas and selected_lma:
                    actions.link_to_lma(selected_smas, selected_lma)
                    db.session.commit()
                    flash("SMA linked to LMA", "success")
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
            data = actions.convert_file_to_df(uploaded_file)
            if data is None:
                actions.file_upload_delete(uploaded_file)
                return redirect(url_for("data_bp.update_data"))
            pm_userid = actions.get_pm_userid(data)
            if pm_userid is None:
                actions.file_upload_delete(uploaded_file)
                return redirect(url_for("data_bp.update_data"))
            file_date = actions.get_file_date(data)
            data = actions.df_cleanup(data)
            update_ta = actions.check_db_ta(data)
            if update_ta:
                db.session.commit()
            update_account_id = actions.get_update_id(file_date)
            if update_account_id is None:
                create.new_update_account_entry(current_user.id, file_date)
                db.session.commit()
                update_account_id = actions.get_update_id(file_date)
            data = actions.df_add_update_id(data, update_account_id)
            off_code = actions.get_off_code(pm_userid)
            data = actions.remove_nfp_smas(data, off_code)
            update_sma = actions.update_smas(
                data, off_code, pm_userid, file_date, update_account_id
            )
            db.session.commit()
            if len(update_sma) > 0:
                update.data_frame_to_sql("sma", update_sma)
            update_lma = actions.update_lmas(
                data, off_code, pm_userid, file_date, update_account_id
            )
            db.session.commit()
            if len(update_lma) > 0:
                update.data_frame_to_sql("lma", update_lma)
            actions.update_rel_mv(pm_userid)
            db.session.commit()
            flash("Database updated.", "success")

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
    form = NewRelationshipForm()
    rel_filter_form = RelationshipFilterForm()
    lma_filter_form = AccountFilterForm()

    if request.method == "GET":
        if "lma_filter" in session:
            lmas = current_user.load_lmas(filter=session["lma_filter"], rel_data=True)
        else:
            lmas = current_user.load_lmas(filter="", rel_data=True)
        if "rel_filter" in session:
            relationships = current_user.load_relationships(
                filter=session["rel_filter"]
            )
        else:
            relationships = current_user.load_relationships(filter="")

    try:
        if request.method == "POST":
            clear_flashes()
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
                if selected_lmas and selected_rel:
                    actions.link_to_rel(selected_lmas, selected_rel)
                    db.session.commit()
                    update.update_relationship_mv(selected_rel)
                    db.session.commit()
                    flash("Account linked to Relationship", "success")
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
