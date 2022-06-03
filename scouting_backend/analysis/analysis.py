from flask import render_template, Blueprint

analysis_bp = Blueprint(
    'analysis_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@analysis_bp.route("/matchSchedule", methods=["GET", "POST"])
def matchSchedule():
    return render_template("matchSchedule.html")
