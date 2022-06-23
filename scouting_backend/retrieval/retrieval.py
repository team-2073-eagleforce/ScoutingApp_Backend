from click import edit
from flask import render_template, Blueprint, request, session, jsonify
from sheet import create_new_sheet, edit_sheet, get_all_sheets
from tba import get_match_team

from .models import db, matchEntry
from scouting_backend.analysis.analysis import db, conn
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


retrieval_bp = Blueprint(
    'retrieval_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

engine = create_engine("postgresql://iovoclgutwvauo:96baff9ff4b4e43005ef48d270eea03a98ff3ab03a1917c35e853e92589bccc4@ec2-52-204-195-41.compute-1.amazonaws.com:5432/d2csu45r67sphs")
db = scoped_session(sessionmaker(bind=engine))
conn = db()
c = conn


@retrieval_bp.route("/qrScanner", methods=["GET", "POST"])
def qrScanner():
    return render_template('QRScanner.html')


@retrieval_bp.route('/detectScan', methods=['POST'])
def test():
    QRData = request.form['data'].split(',')
    print(QRData)
    existing_match = db.execute('SELECT * FROM scouting WHERE team=:team AND "matchNumber"=:matchNumber', {"team": QRData[0], "matchNumber": QRData[1]}).fetchall()

    if len(existing_match) == 0:
        c.execute('INSERT INTO scouting (team, "matchNumber", "autoCrossing", "autoUpper", "autoBottom", "teleUpper", "teleBottom", "level", "driverPerf", "defensePerf", "name", "comment") VALUES (:t, :m, :ac, :au, :ab, :tu, :tb, :l, :dp, :dep, :name, :co)', {
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
            "co": QRData[11]
        })
        conn.commit()

    print("Does it exist? ", existing_match)
    # existing_match = matchEntry.query.filter(matchEntry.team == QRData[0] or matchEntry.matchNumber == QRData[1]).first()
    # if not existing_match:
    #     match = matchEntry(
    #         team=int(QRData[0]),
    #         matchNumber=int(QRData[1]),
    #         autoCrossing=int(QRData[2]),
    #         autoUpper=int(QRData[3]),
    #         autoBottom=int(QRData[4]),
    #         teleUpper=int(QRData[5]),
    #         teleBottom=int(QRData[6]),
    #         level=int(QRData[7]),
    #         driverPerf=int(QRData[8]),
    #         defensePerf=int(QRData[9]),
    #         name=str(QRData[10]),
    #         comment=str(QRData[11]),
    #     )
    #     db.session.add(match)
    #     db.session.commit()

    return render_template('QRScanner.html')


@retrieval_bp.route("/thebluealliance")
def get_match_schedule():
    t = []

    teams = get_match_team("2022cafr")
    for team in teams:
        t.append(int(team["team_number"]))    
    
    t.sort(reverse=True)

    names = []

    for _ in t:
        names["Team" + _]

    # create_new_sheet(session, t)

    return "Success maybe"

@retrieval_bp.route("/testing-sheet-api")
def testing_sheet_api():
    sheets = get_all_sheets(session)
    return jsonify(sheets)

@retrieval_bp.route("/qrScannerV2")
def qrScannerV2():
    return render_template("QRScannerV2.html")

def upload_data_to_sheet(session, data):
    """
    session: flask.session
    data: The qr scanner result, refer to models.py for schema
    """

    sheets = get_all_sheets(session)

    return edit_sheet(session, "Sheet1!A1:A12", data)


    
