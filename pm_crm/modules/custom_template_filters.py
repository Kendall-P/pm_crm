from flask import current_app as app


@app.template_filter("currencyFormat")
def currencyFormat(value):
    value = float(value)
    return "${:,.2f}".format(value)


# @app.template_filter("latestDate")
# def latestDate(meetings):
#     dates = []
#     for i in range(len(meetings)):
#         dates.append(meetings[i].date_updated)
#     dates.sort(reverse=True)

#     if dates:
#         return dates[0].strftime("%m.%d.%y")
#     else:
#         return ""


@app.template_filter("formatDate")
def formatDate(date):
    return date.strftime("%Y-%m-%d")


@app.template_filter("lmaTotal")
def lmaTotal(account):
    total = 0
    total += account.market_value
    if account.sma:
        for n in range(len(account.sma)):
            total += account.sma[n].market_value
    return "${:,.2f}".format(total)
