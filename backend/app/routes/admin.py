from flask import Blueprint, session, render_template
from app.auth.decorators import login_required, role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin")
@login_required
@role_required("ROLE_ADMIN")
def view():
    username = session["user"].get("preferred_username")
    display_name = session["user"].get("nickname")
    return render_template("admin_dashboard.html",
                           username=username, display_name=display_name,
                           current_path='/admin')