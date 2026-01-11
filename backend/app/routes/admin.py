from sqlalchemy import select
from app.db import Session
from app.models import ArtistRequest, User
from flask import Blueprint, session, render_template, current_app, jsonify
from app.utils.decorators import login_required, role_required
from app.utils.user_roles import get_user_roles
from backend.app.utils.opensearch import opensearch
from werkzeug.exceptions import InternalServerError


admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/admin")
@role_required("ROLE_ADMIN")
def view():
    """ View 'Admin' page """

    stmt = select(User, ArtistRequest) \
        .join(ArtistRequest, User.id == ArtistRequest.user_id) \
        .order_by(ArtistRequest.created_at.desc())
    requests = Session.execute(stmt).all()

    return render_template("pages/admin_dashboard.html",
                           admin_console_link=current_app.config['ADMIN_URL'],
                           artist_requests=requests,
                           current_path='/admin',
                           roles=get_user_roles())


@admin_bp.route("/admin/reindex_catalog", methods=["GET"])
@role_required("ROLE_ADMIN")
def reindex_catalog():
    """ Reindex entire catalog from db in OpenSearch """
    try:
        opensearch.reindex_all()
    except RuntimeError as e:
        current_app.logger.error(str(e))
        raise InternalServerError("Reindexing failed. See error log for details.")
    return jsonify(ok=True)
