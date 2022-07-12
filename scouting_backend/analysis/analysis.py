import os

import numpy as np
from flask import jsonify, render_template, Blueprint, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from scouting_backend.helpers import login_required
from scouting_backend.tba import get_match_schedule, get_match_team

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
