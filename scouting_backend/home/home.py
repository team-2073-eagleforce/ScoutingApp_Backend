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

    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid username or password. Please try again!'
        else:
            session['username'] = request.form['username']
            return redirect(url_for('home_bp.dashBoard'))

    return render_template('login.html', error=error)


@home_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home_bp.login'))


@home_bp.route("/dashBoard", methods=["GET", "POST"])
def dashBoard():
    return render_template("dashboard/dashboard.html")
