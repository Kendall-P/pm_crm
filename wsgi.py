from pm_crm import create_app

app = create_app()

if __name__ == "__main__":
    app.run()


"""
TODO - Check - If meeting call occured already this month / overwrite date
TODO - Change Call/Meeting from auto generated to checkbox selection for months - many-to-many needed?
"""
