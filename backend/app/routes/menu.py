from flask import Blueprint, session, render_template
from app.utils.user_roles import get_user_roles


menu_bp = Blueprint('menu', __name__)


@menu_bp.route("/")
def home():
    """ View home page """

    if "user" in session:
        return render_template("pages/search_page.html", current_path='/', roles=get_user_roles())
    return render_template("pages/login.html")
