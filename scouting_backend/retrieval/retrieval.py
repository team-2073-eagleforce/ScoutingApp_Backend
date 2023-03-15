import os
import traceback

from flask import render_template, Blueprint, request, session, jsonify
from scouting_backend.helpers import login_required
from sheet import edit_sheet, get_all_sheets
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tba import get_match_team

from scouting_backend.analysis.analysis import db, conn
from scouting_backend.home.home import CONST_HOME_TEAM
from .models import db
from tba import get_comps
from scouting_backend.constants import CONST_HOME_TEAM, CONST_YEAR
import datetime, json

from ..constants import DNP, PIT_SCOUT_EMAIL

today = datetime.date.today()

from database import load_json

retrieval_bp = Blueprint(
    'retrieval_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

engine = create_engine("postgresql://" + os.getenv("DATABASE_URL").split("://")[1])
db = scoped_session(sessionmaker(bind=engine))
conn = db()
c = conn
comps = get_comps(CONST_HOME_TEAM, CONST_YEAR)

@retrieval_bp.route("/qrScanner", methods=["GET", "POST"])
@login_required
def qrScanner():
    if session.get("email") in PIT_SCOUT_EMAIL:
        return "Unauthorized. As a pit scout, you can only view the <a href='/analysis/team>'teams page</a> or submit <a href='/pit/scout/2023>'pit scouting data</a>"
    return render_template('QRScanner.html', comps=comps)


@retrieval_bp.route('/detectScan', methods=['POST'])
@login_required
def detectScan():
    return redirect(f"/detectScan/{year}")


@retrieval_bp.route('/detectScan/2023', methods=['POST'])
@login_required
def detect_scan_2023():
    session["errordata"] = request.form["data"]
    print(request.form["data"].split("'"))
    json_data = json.loads(request.form["data"].split("'")[0])
    load_json(json_data)
    return render_template('QRScanner.html', comps=comps)

@retrieval_bp.route('/detectScan/2022', methods=['POST'])
@login_required
def detect_scan_2022():
    QRData = request.form['data'].split(',')
    if QRData[12] == "2022caelk":
        QRData[12] = "2022cacc"

    print(QRData)
    existing_match = db.execute('SELECT * FROM scouting WHERE team=:team AND "matchnumber"=:matchNumber AND "comp_code"=:comp', {"team": QRData[0], "matchNumber": QRData[1], "comp": QRData[12]}).fetchall()

    if len(existing_match) == 0:
        c.execute('INSERT INTO scouting (team, "matchnumber", "autocrossing", "autoupper", "autobottom", "teleupper", "telebottom", "level", "driverperf", "defenseperf", "name", "comment", "comp_code") VALUES (:t, :m, :ac, :au, :ab, :tu, :tb, :l, :dp, :dep, :name, :co, :comp)', {
            "t": QRData[0],
            "m": QRData[1],
            "ac": QRData[2],
            "au": QRData[3],
            "ab": QRData[4],
            "tu": QRData[5],
            "tb": QRData[6],
            "l": QRData[7],
            "dp": QRData[8],
            "dep": QRData[9],
            "name": QRData[10],
            "co": QRData[11],
            "comp": QRData[12],
        })
        conn.commit()

    print("Does it exist? ", existing_match)

    return render_template('QRScanner.html', comps=comps)

@retrieval_bp.route("/thebluealliance")
def get_match_schedule():
    t = []

    teams = get_match_team("2022cafr")
    for team in teams:
        t.append(int(team["team_number"]))    
    
    t.sort(reverse=True)
    print(t)
    names = []

    for _ in t:
        names["Team" + str(_)]

    # create_new_sheet(session, t)

    return "Success maybe"

@retrieval_bp.route("/testing-sheet-api")
def testing_sheet_api():
    sheets = get_all_sheets(session)
    return jsonify(sheets)

def upload_data_to_sheet(session, data):
    """
    session: flask.session
    data: The qr scanner result, refer to models.py for schema
    """

    sheets = get_all_sheets(session)

    return edit_sheet(session, "Sheet1!A1:A12", data)
