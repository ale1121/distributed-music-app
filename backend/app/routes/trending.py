from flask import Blueprint, session, render_template
from app.utils.decorators import login_required, role_required
from app.utils.user_roles import get_user_roles


trending_bp = Blueprint('trending', __name__)


@trending_bp.route("/trending")
def view():
    """ View trending page """

    if "user" in session:
        return render_template("layout/app_layout.html", current_path='/trending', roles=get_user_roles())
    return render_template("pages/login.html")
