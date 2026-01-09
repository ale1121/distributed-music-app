from flask import Blueprint, session, render_template
from app.utils.user_roles import get_user_roles


home_bp = Blueprint('home', __name__)


@home_bp.route("/")
def view():
    """ View home page """

    if "user" in session:
        return render_template("pages/search_page.html", current_path='/', roles=get_user_roles())
    return render_template("pages/login.html")
