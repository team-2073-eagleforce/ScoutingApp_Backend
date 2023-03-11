import os
from flask import Blueprint, render_template, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from scouting_backend.home.home import CONST_HOME_TEAM, CONST_YEAR
from scouting_backend.helpers import login_required, upload_image

from .models import PitEntry, db
from scouting_backend.tba import get_comps

engine = create_engine("postgresql://" + os.getenv("DATABASE_URL").split("://")[1])
db = scoped_session(sessionmaker(bind=engine))
conn = db()
c = conn

pit_bp = Blueprint(
    'pit_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@pit_bp.route("/scout/2022", methods=["GET", "POST"])
@login_required
def pit_submit():
    if request.method == "POST":
        res = c.execute("SELECT * FROM PitEntry WHERE team=:team AND comp_code=:comp", {
            "team": request.form["team"],
            "comp": request.form["comp"]
        }).fetchall()

        if len(res) != 0:
            return "This data is submitted already"

        robot_image_url = upload_image(request.files.getlist('pic')[0])
        print(robot_image_url)
        # robot_image_url = "https://google.com/"

        print(request.form)

        c.execute("INSERT INTO PitEntry (team, comp_code, drive_train, robot_type, prefer_to_score, hub, auto, climb, comments, submitted_by, image_url) VALUES (:team, :comp, :drivetrain, :type, :score, :hub, :auto, :climb, :comments, :submitted_by, :img_url)", {
            "team": request.form["team"],
            "comp": request.form["comp"],
            "drivetrain": request.form["drivetrain"],
            "type": request.form["type"],
            "score": request.form["score"],
            "hub": request.form["place"],
            "auto": ", ".join(request.form.getlist("auto")),
            "climb": request.form["climb"],
            "comments": request.form["comment"],
            "submitted_by": session.get("name"),
            "img_url": robot_image_url
        })  
        conn.commit()
        return "Done"
    else:
        return render_template("2023/form.html", comps=get_comps(CONST_HOME_TEAM, CONST_YEAR))


@pit_bp.route("/scout/2023", methods=["GET", "POST"])
@login_required
def pit_submit_2023():
    if request.method == "POST":
        res = c.execute("SELECT * FROM pit_scouting_2023 WHERE team_number=:team AND comp_code=:comp", {
            "team": request.form["team"],
            "comp": request.form["comp"]
        }).fetchall()

        if len(res) != 0:
            return "This data is submitted already"

        auto_abilities = ", ".join(request.form.getlist("auto-abilities"))
        prefered_gp = ", ".join(request.form.getlist("prefered-gp"))
        cannot_pu = ", ".join(request.form.getlist("cannot-gp"))
        cone_pu = ", ".join(request.form.getlist("cone-pu"))
        cube_pu = ", ".join(request.form.getlist("cube-pu"))

        robot_image_url = upload_image(request.files.getlist('pic')[0])

        c.execute("INSERT INTO pit_scouting_2023 (comp_code, img_url, drive_train, robot_type, weight, drivetrain_velocity, preferred_game_piece, cannot_pick_up, cone_pick_up, cube_pick_up, auto_position, auto_abilities, name, team_number) VALUES (:comp, :img, :drivetrain, :robot_type, :weight, :drivetrain_velocity, :pgp, :cannotpu, :conepu, :cubepu, :autopos, :autoab, :name, :team)", {
            "comp": request.form["comp"],
            "img": robot_image_url,
            "drivetrain": request.form["drivetrain"],
            "robot_type": request.form["type"],
            "weight": request.form["weight"],
            "drivetrain_velocity": request.form["vel"],
            "pgp": prefered_gp,
            "cannotpu": cannot_pu,
            "conepu": cone_pu,
            "cubepu": cube_pu,
            "autopos": request.form["autopos"],
            "autoab": auto_abilities,
            "name": session.get("name"),
            "comment": request.form["comment"],
            "team": request.form["team"]
        })
        conn.commit()

        return "Scouting data submitted successfully, click to <a href='/pit/scout/2023'>here</a> to go back to Pit Scouting form."
    
    else:
        return render_template("2023/form.html", comps=get_comps(CONST_HOME_TEAM, CONST_YEAR))


@pit_bp.route("/analysis")
def pit_analysis():
    entries = c.execute("SELECT * FROM PitEntry;").fetchall()
    return render_template("pit-analysis.html", entries=entries)

