from flask import jsonify, render_template, Blueprint, request, session, redirect, url_for
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import os
from scouting_backend.tba import get_match_schedule, get_comps

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient import discovery
from scouting_backend import sheet

from scouting_backend.constants import AUTHORIZED_EMAIL
from helpers import login_required

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']

client_config = {
    "web": {
        "client_id": "351274848173-0eepc6g5hc4ri03l67rql056p7e6g8nv.apps.googleusercontent.com",
        "project_id": "scouting-excel-test",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": [
            "https://google-sheet-interaction.boyuan12.repl.co/oauth2callback",
            "http://google-sheet-interaction.boyuan12.repl.co/oauth2callback",
            "https://team2073-scouting.herokuapp.com/analysis/oauth2callback",
            "http://team2073-scouting.herokuapp.com",
            "http://127.0.0.1:5001/analysis/oauth2callback"
        ],
        "javascript_origins": [
            "https://google-sheet-interaction.boyuan12.repl.co",
            "https://team2073-scouting.herokuapp.com",
            "http://127.0.0.1:5001"
        ]
    }
}

analysis_bp = Blueprint(
    'analysis_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

engine = create_engine(
    "postgresql://iovoclgutwvauo:96baff9ff4b4e43005ef48d270eea03a98ff3ab03a1917c35e853e92589bccc4@ec2-52-204-195-41.compute-1.amazonaws.com:5432/d2csu45r67sphs")
db = scoped_session(sessionmaker(bind=engine))
conn = db()

CONST_CLIMB_POINTS = [0, 4, 6, 10, 15]
CONST_AUTO_CROSS = [0, 2]
CONST_HOME_TEAM = 2073

@login_required
@analysis_bp.route("/matchSchedule", methods=["GET", "POST"])
def matchSchedule():
    return render_template("dashboard/matchSchedule.html")

@login_required
@analysis_bp.route("/team/<int:team>", methods=["GET"])
def view_team_data(team):
    matches = db.execute("SELECT * FROM scouting WHERE team=:team", {"team": team})
    return render_template("team.html", matches=matches, team=team)

@login_required
@analysis_bp.route("/sheet")
def google_sheet_rendering():
    return render_template("sheet.html")

@login_required
@analysis_bp.route("/edit-sheet")
def edit_sheet():
    """
    range_: cell we want to modify
    value_range_body = {
        "values": [
            [
                "value to update"
            ]
        ]
    }
    """
    if 'credentials' not in session:
        return redirect('authorize')

    response = sheet.edit_sheet(session, "Sheet1!B5", "Hello World")

    return jsonify(**response)


@analysis_bp.route("/authorize")
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('analysis_bp.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)


@analysis_bp.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('analysis_bp.oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    cred = credentials_to_dict(credentials)
    session['credentials'] = cred

    r = requests.get(f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={cred["token"]}').json()
    
    print(r)

    session["name"] = r["given_name"] + " " + r["family_name"]

    if r["email"] not in AUTHORIZED_EMAIL:
        return "405 UNAUTHORIZED"

    session["email"] = r["email"]

    return redirect(url_for('analysis_bp.google_sheet_rendering'))


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


@analysis_bp.route("/api/get_match_schedule/<string:event_key>/<string:match_num>")
def api_get_match_schedule(event_key, match_num):
    # {"red": ["frc1", "frc2", "frc3"], "blue": ["frc4", "frc5", "frc6"]}
    teams_in_match = get_match_schedule(event_key, int(match_num))
    positions = ['red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']
    averages_for_teams_in_match = dict(zip(positions, calculate_averages(tuple(pos.split('frc')[1] for pos in teams_in_match['red'] + teams_in_match['blue']))))

    return jsonify(averages_for_teams_in_match)


def calculate_averages(teams):
    matches_for_team = db.execute("""SELECT * FROM scouting WHERE team IN {teams}""".format(teams=teams)).fetchall()
    dic_matches_for_team = dict(zip(teams, ([int(teams[team])] + [0] * 7 for team in range(len(teams)))))

    for match in matches_for_team:
        team_sum = dic_matches_for_team[str(match[1])]

        climb_points = CONST_CLIMB_POINTS[match[8]]
        tele_lower_points = match[7]
        tele_upper_points = match[6] * 2
        auto_lower_points = match[5] * 2
        auto_upper_points = match[4] * 4
        auto_cross_points = CONST_AUTO_CROSS[match[3]]

        team_sum[1] += match[4]
        team_sum[2] += match[5]
        team_sum[3] += match[6]
        team_sum[4] += match[7]
        team_sum[5] += match[8]
        team_sum[6] += climb_points + tele_upper_points + tele_lower_points + auto_upper_points + auto_lower_points + auto_cross_points
        team_sum[7] += 1

    all_averages = []
    for averages in dic_matches_for_team.values():
        average_div = [averages[0]]
        for data_val in averages[1:-1]:
            if averages[-1] == 0:
                averages[-1] = 1
            average_div.append(round(data_val/averages[-1], 2))
        all_averages.append(average_div)
    return all_averages

@analysis_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def analysis_dashboard():
    comps = get_comps(CONST_HOME_TEAM, 2022)
    return render_template("dashboard/dashboard.html", comps=comps)
