from flask import render_template, Blueprint, request

from .models import db, matchEntry

retrieval_bp = Blueprint(
    'retrieval_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@retrieval_bp.route("/qrScanner", methods=["GET", "POST"])
def qrScanner():
    return render_template('QRScanner.html')


@retrieval_bp.route('/detectScan', methods=['POST'])
def test():
    QRData = request.form['data'].split(',')
    existing_match = matchEntry.query.filter(matchEntry.team == QRData[0] or matchEntry.matchNumber == QRData[1]).first()
    if not existing_match:
        match = matchEntry(
            team=int(QRData[0]),
            matchNumber=int(QRData[1]),
            autoCrossing=int(QRData[2]),
            autoUpper=int(QRData[3]),
            autoBottom=int(QRData[4]),
            teleUpper=int(QRData[5]),
            teleBottom=int(QRData[6]),
            level=int(QRData[7]),
            driverPerf=int(QRData[8]),
            defensePerf=int(QRData[9]),
            name=str(QRData[10]),
            comment=str(QRData[11]),
        )
        db.session.add(match)
        db.session.commit()
    return render_template('QRScanner.html')
