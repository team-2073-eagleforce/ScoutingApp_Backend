import os

import numpy as np
from flask import jsonify, render_template, Blueprint, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from scouting_backend.helpers import login_required
from scouting_backend.tba import get_match_schedule, get_match_team, get_comps
from scouting_backend.constants import CONST_HOME_TEAM, CONST_YEAR

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

comps = get_comps(CONST_HOME_TEAM, CONST_YEAR)

def get_teams_at_event(event):
    print(event)
    return tuple(int(team['team_number']) for team in get_match_team(event))

@login_required
@analysis_bp.route("/team")
def team_navigation():
    comp = request.args.get("code")

    # In case someone visited /team directly, which requires a query string code, for error catching
    if comp is None:
        all_teams = []
        team_and_image = []
        results = []
    else:
        all_teams = get_teams_at_event(comp)
        team_and_image = db.execute("""SELECT team, image_url FROM PitEntry WHERE team IN {teams}""".format(teams=all_teams)).fetchall()
        results = {team[0]: team[1] for team in team_and_image}

    return render_template("teams_navigation.html", teams=results, all_teams=all_teams, comps=comps)

@login_required
@analysis_bp.route("/team/<int:team>", methods=["GET"])
def view_team_data(team):
    comp_code = request.args.get("code")
    matches = db.execute("SELECT * FROM scouting WHERE team=:team AND comp_code=:comp ORDER BY matchnumber ASC", {"team": team, "comp": comp_code})
    pit = db.execute("SELECT * FROM PitEntry WHERE team=:team AND comp_code=:comp", {"team": team, "comp": comp_code}).fetchall()
    matches_with_calculated_scores = []

    for match in matches:
        convert_match_to_list = list(match)
        points_per_section = calculate_points(match)
        convert_match_to_list.insert(6, points_per_section[0])
        convert_match_to_list.insert(9, points_per_section[1])
        convert_match_to_list.insert(11, points_per_section[2])
        convert_match_to_list.insert(12, points_per_section[3])

        matches_with_calculated_scores.append(convert_match_to_list)
    
    if len(pit) == 0:
        pit = [["N/A" for i in range(12)]]
    return render_template("team.html", matches=matches_with_calculated_scores, team=team, comps=comps, pit=pit)


@login_required
@analysis_bp.route("/rankings", methods=['GET', 'POST'])
def rankings_list():
    comp = request.args.get("code")
    if comp is None:
        all_teams = []
        dic_team_with_average = {}
    else:
        all_teams = get_teams_at_event(comp)
        team_with_selected_data_values = db.execute("""SELECT * FROM scouting WHERE team IN {teams}""".format(teams=all_teams)).fetchall()

        dic_team_with_average = dict(zip(all_teams, ([0] * 7 for team in range(len(all_teams)))))
        for match in team_with_selected_data_values:
            team_score = dic_team_with_average[match[1]]

            calculated_scores = calculate_points(match)
            team_score[0] += calculated_scores[0]
            team_score[1] += calculated_scores[1]
            team_score[2] += calculated_scores[2]
            team_score[3] += calculated_scores[3]
            team_score[4] += match[9]
            team_score[5] += match[10]
            team_score[6] += 1

        for score_sum in dic_team_with_average.values():
            if score_sum[-1] == 0:
                score_sum[-1] = 1
            for score_index in range(len(score_sum[:-1])):
                score_sum[score_index] = (round(score_sum[score_index] / score_sum[-1], 2))
        print(dic_team_with_average)
    return render_template("rankings.html", calculated_averages=dic_team_with_average, comps=comps)


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

@login_required
@analysis_bp.route("/dashboard", methods=['GET', 'POST'])
def analysis_dashboard():
    return render_template("dashboard.html", comps=comps)
