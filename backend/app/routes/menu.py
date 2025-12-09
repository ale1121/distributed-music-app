from flask import Blueprint, session, render_template
from app.auth.decorators import login_required, role_required


menu_bp = Blueprint('menu', __name__)


@menu_bp.route("/")
def home():
    if "user" in session:
        username = session["user"].get("preferred_username", "User")
        roles = session["user"].get("realm_access", {}).get("roles", [])
        role_info = ", ".join(roles) if roles else "No roles"

        return render_template("search_page.html", current_path='/')
    return render_template("login_page.html")
