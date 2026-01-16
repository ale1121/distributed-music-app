from sqlalchemy import select
from flask import Blueprint, render_template, current_app
from app.database.db import Session
from app.database.models import ArtistRequest, User
from app.auth.decorators import role_required
from app.auth.auth_ctx import get_user_roles


admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/admin", methods=["GET"])
@role_required("ROLE_ADMIN")
def view():
    """ View Admin page """

    stmt = select(User, ArtistRequest) \
        .join(ArtistRequest, User.id == ArtistRequest.user_id) \
        .order_by(ArtistRequest.created_at.desc())
    requests = Session.execute(stmt).all()

    return render_template("pages/admin_dashboard.html",
                           admin_console_link=current_app.config['ADMIN_URL'],
                           artist_requests=requests,
                           current_path='/admin',
                           roles=get_user_roles())
