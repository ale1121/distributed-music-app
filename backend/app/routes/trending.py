from flask import Blueprint, render_template, current_app
from app.auth.decorators import login_required
from app.auth.auth_ctx import get_user_roles


trending_bp = Blueprint('trending', __name__)


@trending_bp.route("/trending")
@login_required
def view():
    """ View trending page """

    gf_url = current_app.config['GRAFANA_URL']
    gf_dashboard = current_app.config['GRAFANA_DASHBOARD']

    return render_template("pages/trending_page.html",
                           gf_url=gf_url,
                           gf_dashboard=gf_dashboard,
                           current_path='/trending',
                           roles=get_user_roles())
