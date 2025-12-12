from flask import Blueprint, session, render_template
from app.decorators import login_required, role_required


trending_bp = Blueprint('trending', __name__)


@trending_bp.route("/trending")
def view():
    if "user" in session:
        return render_template("base_main.html", current_path='/trending')
    return render_template("login_page.html")
