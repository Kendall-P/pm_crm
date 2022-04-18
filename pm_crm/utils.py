from flask import session


def clear_flashes():
    try:
        session["_flashes"].clear()
    except KeyError:
        pass
