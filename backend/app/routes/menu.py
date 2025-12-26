from flask import Blueprint, session, render_template


menu_bp = Blueprint('menu', __name__)


@menu_bp.route("/")
def home():
    """ View home page """

    if "user" in session:
        return render_template("pages/search_page.html", current_path='/')
    return render_template("pages/login.html")
