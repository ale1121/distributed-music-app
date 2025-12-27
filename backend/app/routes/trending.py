from flask import Blueprint, session, render_template
from app.utils.decorators import login_required, role_required


trending_bp = Blueprint('trending', __name__)


@trending_bp.route("/trending")
def view():
    """ View trending page """

    if "user" in session:
        return render_template("layout/app_layout.html", current_path='/trending')
    return render_template("pages/login.html")
