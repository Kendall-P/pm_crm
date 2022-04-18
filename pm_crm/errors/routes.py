from flask import Blueprint, make_response, render_template

error_bp = Blueprint(
    "error_bp", __name__, template_folder="templates", static_folder="static"
)

# @error_bp.errorhandler(400)
# def bad_request():
#     """Bad request."""
#     return make_response(render_template("400.html"), 400)


# @error_bp.errorhandler(404)
# def not_found():
#     """Page not found."""
#     return make_response(render_template("404.html"), 404)


# @error_bp.errorhandler(500)
# def server_error():
#     """Internal server error."""
#     return make_response(render_template("500.html"), 500)
