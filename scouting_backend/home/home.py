from flask import render_template, request, redirect, url_for, session, Blueprint

home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@home_bp.route("/", methods=['GET', 'POST'])
@home_bp.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    return render_template('login.html', error=error)
