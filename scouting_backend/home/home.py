from flask import render_template, request, redirect, url_for, session, Blueprint

from scouting_backend.tba import get_comps
from scouting_backend.constants import CONST_HOME_TEAM, CONST_YEAR

home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@home_bp.route("/", methods=['GET', 'POST'])
@home_bp.route("/login", methods=['GET', 'POST'])
def login():
    comps = get_comps(CONST_HOME_TEAM, CONST_YEAR)
    error = None
    return render_template('login.html', error=error, comps=comps)
