from flask import current_app as app


@app.template_filter("currencyFormat")
def currencyFormat(value):
    value = float(value)
    return "${:,.2f}".format(value)
