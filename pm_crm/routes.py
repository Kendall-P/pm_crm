from flask import current_app as app, make_response
from flask import render_template, flash, url_for


@app.route("/")
def home():
    return render_template("home.html")
