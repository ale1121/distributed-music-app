from sqlalchemy import select
from app.db import Session
from app.models import ArtistRequest, User
from flask import Blueprint, session, render_template, current_app, jsonify
from app.decorators import login_required, role_required


admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/admin")
@role_required("ROLE_ADMIN")
def view():
    """ View 'Admin' page """

    stmt = select(User, ArtistRequest).join(ArtistRequest, User.id == ArtistRequest.user_id)
    requests = Session.execute(stmt).all()

    current_app.logger.debug(f"---REQUESTS: {requests}")

    return render_template("admin_dashboard.html",
                           admin_console_link=current_app.config['ADMIN_URL'],
                           artist_requests=requests,
                           current_path='/admin')
