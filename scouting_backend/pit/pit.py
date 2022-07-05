import os
from flask import Blueprint, render_template, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from scouting_backend.analysis.analysis import CONST_HOME_TEAM
from scouting_backend.helpers import upload_image

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


@pit_bp.route("/", methods=["GET", "POST"])
def pit_submit():
    if request.method == "POST":
        print("LOOL")
        res = c.execute("SELECT * FROM PitEntry WHERE team=:team AND comp_code=:comp", {
            "team": request.form["team"],
            "comp": request.form["comp"]
        }).fetchall()
        print("THE COEE IS SUIO:I TO OWRKOSI BUT IST SLKN")

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
        return render_template("form.html", comps=get_comps(CONST_HOME_TEAM, 2022))


@pit_bp.route("/analysis")
def pit_analysis():
    entries = c.execute("SELECT * FROM PitEntry;").fetchall()
    return render_template("pit-analysis.html", entries=entries)

