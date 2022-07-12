from flask import jsonify, render_template, Blueprint, request, session, redirect, url_for
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import os
from scouting_backend.tba import get_match_schedule, get_match_team


import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient import discovery
from scouting_backend import sheet

import json

import numpy as np
from scouting_backend.constants import AUTHORIZED_EMAIL
from scouting_backend.helpers import login_required

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
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
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

engine = create_engine("postgresql://" + os.getenv("DATABASE_URL").split("://")[1])
db = scoped_session(sessionmaker(bind=engine))
conn = db()

CONST_CLIMB_POINTS = [0, 4, 6, 10, 15]
CONST_AUTO_CROSS = [0, 2]


def get_teams_at_event(event):
    return tuple(int(team['team_number']) for team in get_match_team(event))

@login_required
@analysis_bp.route("/team")
def team_navigation():
    comp = request.args.get("code")

    # In case someone visited /team directly, which requires a query string code, for error catching
    if comp == None:
        all_teams = []
        team_and_image = []
    else:
        all_teams = get_teams_at_event(comp)
        team_and_image = db.execute("""SELECT team, image_url FROM PitEntry WHERE team IN {teams}""".format(teams=all_teams)).fetchall()
    return render_template("teams_navigation.html", teams=team_and_image)

@login_required
@analysis_bp.route("/team/<int:team>", methods=["GET"])
def view_team_data(team):
    matches = db.execute("SELECT * FROM scouting WHERE team=:team", {"team": team})
    matches_with_calculated_scores = []

    for match_num, match in enumerate(matches):
        convert_match_to_list = list(match)
        points_per_section = calculate_points(match)
        convert_match_to_list.insert(6, points_per_section[0])
        convert_match_to_list.insert(9, points_per_section[1])
        convert_match_to_list.insert(11, points_per_section[2])
        convert_match_to_list.insert(12, points_per_section[3])

        matches_with_calculated_scores.append(convert_match_to_list)
    return render_template("team.html", matches=matches_with_calculated_scores, team=team)

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

    return redirect('/')

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

@analysis_bp.route("/rankings", methods=['GET', 'POST'])
def rankings_list():
    return render_template("rankings.html")


@analysis_bp.route("/sorter", methods=['GET', 'POST'])
def sorter():
    sort_by = request.form['button_selected']
    all_teams = get_teams_at_event("2022cafr")
    team_data_for_selected = dict(zip(all_teams, fetch_sql_for_rankings(all_teams, sort_by)))
    return jsonify(team_data_for_selected)


def fetch_sql_for_rankings(all_teams, sort_by):
    corresponding_data_fields = {'by_auto': '"team", "autocrossing", "autoupper", "autobottom"', 'by_teleop': '"team", "teleupper", "telebottom"',
         'by_climb': '"team", "level"', 'by_total': '"team", "autocrossing", "autoupper", "autobottom", "teleupper", "telebottom", "level"'}

    team_with_selected_data_values = db.execute("""SELECT {sort_by} FROM scouting WHERE team IN {teams}""".format(sort_by=corresponding_data_fields[sort_by], teams=all_teams)).fetchall()
    dic_team_with_average = dict(zip(all_teams, ([0] * 2 for team in range(len(all_teams)))))

    for match in team_with_selected_data_values:
        score_points = [[0, 2, 4, 2], [0, 2, 1], [0, 2, 4, 2, 2, 1, 0]]
        team_score_for_datatype = dic_team_with_average[match[0]]

        if sort_by == "by_auto":
            team_score_for_datatype[0] += sum(np.multiply(match, score_points[0]))
        elif sort_by == "by_teleop":
            team_score_for_datatype[0] += sum(np.multiply(match, score_points[1]))
        elif sort_by == "by_climb":
            team_score_for_datatype[0] += CONST_CLIMB_POINTS[match[1]]
        elif sort_by == "by_total":
            team_score_for_datatype[0] += sum(np.multiply(match, score_points[2])) + CONST_CLIMB_POINTS[match[6]]
        team_score_for_datatype[1] += 1

    average_score_for_field = []
    for score_sum in dic_team_with_average.values():
        if score_sum[1] == 0:
            score_sum[1] = 1
        average_score_for_field.append(round(score_sum[0] / score_sum[1], 2))

    return average_score_for_field


@analysis_bp.route("/api/get_match_schedule/<string:event_key>/<string:match_num>")
def api_get_match_schedule(event_key, match_num):
    # {"red": ["frc1", "frc2", "frc3"], "blue": ["frc4", "frc5", "frc6"]}
    teams_in_match = get_match_schedule(event_key, int(match_num))
    positions = ['red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']
    averages_for_teams_in_match = dict(zip(positions, fetch_sql_for_dashboard(tuple(pos.split('frc')[1] for pos in teams_in_match['red'] + teams_in_match['blue']))))

    return jsonify(averages_for_teams_in_match)


def fetch_sql_for_dashboard(teams):
    matches_for_team = db.execute("""SELECT * FROM scouting WHERE team IN {teams}""".format(teams=teams)).fetchall()
    dic_matches_for_team = dict(zip(teams, ([int(teams[team])] + [0] * 7 for team in range(len(teams)))))

    for match in matches_for_team:
        team = dic_matches_for_team[str(match[1])]

        calculated_points_per_section = calculate_points(match)

        team[1] += match[4]
        team[2] += match[5]
        team[3] += match[6]
        team[4] += match[7]
        team[5] += match[8]
        team[6] += calculated_points_per_section[3]
        team[7] += 1

    return calculate_average(dic_matches_for_team)


def calculate_average(sum_of_data):
    all_averages = []
    for averages in sum_of_data.values():
        average_div = [averages[0]]
        for data_val in averages[1:-1]:
            if averages[-1] == 0:
                averages[-1] = 1
            average_div.append(round(data_val/averages[-1], 2))
        all_averages.append(average_div)
    return all_averages


def calculate_points(match):
    points_per_section = []

    auto_cross_points = CONST_AUTO_CROSS[match[3]]
    auto_upper_points = match[4] * 4
    auto_lower_points = match[5] * 2
    tele_upper_points = match[6] * 2
    tele_lower_points = match[7]
    climb_points = CONST_CLIMB_POINTS[match[8]]

    points_per_section.append(auto_cross_points + auto_upper_points + auto_lower_points)
    points_per_section.append(tele_upper_points + tele_lower_points)
    points_per_section.append(climb_points)
    points_per_section.append(sum(points_per_section))

    return points_per_section

@analysis_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def analysis_dashboard():
    return render_template("dashboard.html")
