from flask import Blueprint, session, render_template
from app.auth.decorators import login_required, role_required


trending_bp = Blueprint('trending', __name__)


@trending_bp.route("/trending")
def view():
    if "user" in session:
        username = session["user"].get("preferred_username", "User")
        roles = session["user"].get("realm_access", {}).get("roles", [])
        role_info = ", ".join(roles) if roles else "No roles"

        return render_template("base_main.html", current_path='/trending')
    return render_template("login_page.html")
