import os

import numpy as np
from flask import jsonify, render_template, Blueprint, request, redirect, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from scouting_backend.helpers import login_required
from scouting_backend.tba import get_match_schedule, get_match_team, get_comps, get_offseason_bots, get_team_name
from scouting_backend.constants import CONST_HOME_TEAM, CONST_YEAR, MADTOWN_2022_OFFSEASON_BOTS
import datetime
import json
from termcolor import colored

from helpers import team_data, grid_score
from database import fetch

from constants import DNP, PIT_SCOUT_EMAIL

today = datetime.date.today()

analysis_bp = Blueprint(
    'analysis_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

engine = create_engine("postgresql://" + os.getenv("DATABASE_URL").split("://")[1])
db = scoped_session(sessionmaker(bind=engine))
conn = db()
c = conn

CONST_CLIMB_POINTS = [0, 4, 6, 10, 15]
CONST_AUTO_CROSS = [0, 2]

comps = get_comps(CONST_HOME_TEAM, CONST_YEAR)

def get_teams_at_event(event):
    # elif event == "2022cacc":
    #     return (2288, 5430, 4698, 3598, 5274, 1662, 3189, 8060, 3257, 5458, 4643, 701, 1678, 6918, 3859, 2073, 9973, 5817, 2135, 841, 6662, 6884, 5940, 8048, 2643, 6059, 7777, 199, 1072, 114, 7419, 5924, 7528, 2551, 1671)
    return tuple(set(tuple(int(team['team_number']) for team in get_match_team(event))))

def get_pitscouted_teams(event):
    have_been_pitscouted = []
    for team in get_teams_at_event(event):
        pit = db.execute("SELECT * FROM pit_scouting_2023 WHERE team_number=:team AND comp_code=:comp", {"team": team, "comp": event}).fetchall()
        if(len(pit) != 0):
            have_been_pitscouted.append(int(team))
    return have_been_pitscouted

@analysis_bp.route("/team")
@login_required
def team_navigation():
    comp = request.args.get("code")
    if comp == "test" or comp =="testing":
        all_teams = [i+1 for i in range(1)]
        team_and_image = []
        results = []
        been_pitscouted = []
    # In case someone visited /team directly, which requires a query string code, for error catching
    elif comp is None:
        all_teams = []
        been_pitscouted = []
        team_and_image = []
        results = []
    else:
        all_teams = get_teams_at_event(comp)
        been_pitscouted = get_pitscouted_teams(comp)
        # team_names = []
        # for team in list(all_teams):
        #     team_names.append(get_team_name(team))
        # data = {all_teams[i]: team_names[i] for i in range(len(all_teams))}
        # print(data)

        # team_and_image = db.execute("""SELECT team, image_url FROM PitEntry WHERE team IN {teams} AND comp_code='{comp}'""".format(
        #     teams=all_teams, comp=comp)).fetchall()
        # results = {team[0]: team[1] for team in team_and_image}

    return render_template("teams_navigation.html", all_teams=all_teams, comps=comps, been_pitscouted=been_pitscouted) # all_teams=all_teams, comps=comps)


# @analysis_bp.route("/team/<int:team>", methods=["GET"])
# @login_required
# def view_team_data(team):
#     return redirect(f"/analysis/team/{today.year}/{team}")

@analysis_bp.route("/team/2022/<int:team>", methods=["GET"])
@login_required
def view_team_data_2022(team):
    comp_code = request.args.get("code")
    matches = db.execute(
        "SELECT * FROM scouting WHERE team=:team AND comp_code=:comp ORDER BY matchnumber ASC", {"team": team, "comp": comp_code})
    pit = db.execute("SELECT * FROM PitEntry WHERE team=:team AND comp_code=:comp",
                     {"team": team, "comp": comp_code}).fetchall()
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

    return render_template("team.html", matches=two_people(matches_with_calculated_scores), team=team, comps=comps, pit=pit)


@analysis_bp.route("/team/<int:team>", methods=["GET"])
@login_required
def view_team_data_2023(team):
    comp_code = request.args.get("code")
    matches = db.execute(
        "SELECT * FROM scouting_2023 WHERE team_number=:team AND comp_code=:comp ORDER BY match_number ASC", {"team": team, "comp": comp_code}).fetchall()
    
    data = [] # [[match num, alow, amid, atop, aclimb, tlow, tmid, ttop, tcone, tcube, eclimb, drivep, defp, name, comment]]

    for m in matches:
        # tuple(m) + ()
        team_d = []
        auto_grid = json.loads(json.loads(m[3]))
        teleop_grid = json.loads(json.loads(m[5]))
        print("autogrid   " + str(auto_grid))

        team_d.append(m[2])
        team_d.append(f"{len([x for x in auto_grid[2] if int(x) == 1]) + len([x for x in auto_grid[2] if int(x) == 6])} - {len([x for x in auto_grid[2] if int(x) == 2]) + len([x for x in auto_grid[2] if int(x) == 7])}") # 3 -> two cones, 5 -> cone/cube, 4 -> two cubes, 7 -> cube, 6 -> cone
 
        team_d.append(f"{len([x for x in auto_grid[1] if int(x) == 1]) + len([x for x in auto_grid[1] if int(x) == 6])} - {len([x for x in auto_grid[1] if int(x) == 2]) + len([x for x in auto_grid[1] if int(x) == 7])}") # 3 -> two cones, 5 -> cone/cube, 4 -> two cubes, 7 -> cube, 6 -> cone
 
        team_d.append(f"{len([x for x in auto_grid[0] if int(x) == 1]) + len([x for x in auto_grid[0] if int(x) == 6])} - {len([x for x in auto_grid[0] if int(x) == 2]) + len([x for x in auto_grid[0] if int(x) == 7])}") # 3 -> two cones, 5 -> cone/cube, 4 -> two cubes, 7 -> cube, 6 -> cone

        team_d.append(m[4])
        team_d.append(f"{len([x for x in teleop_grid[2] if int(x) == 1]) + len([x for x in teleop_grid[2] if int(x) == 3])*2 + len([x for x in teleop_grid[2] if int(x) == 5]) + len([x for x in teleop_grid[2] if int(x) == 6])} - {len([x for x in teleop_grid[2] if int(x) == 2]) + len([x for x in teleop_grid[2] if int(x) == 5]) + len([x for x in teleop_grid[2] if int(x) == 4])*2 + len([x for x in teleop_grid[2] if int(x) == 7])}") # 3 -> two cones, 5 -> cone/cube, 4 -> two cubes, 7 -> cube, 6 -> cone
        team_d.append(f"{len([x for x in teleop_grid[1] if int(x) == 1]) + len([x for x in teleop_grid[1] if int(x) == 3])*2 + len([x for x in teleop_grid[1] if int(x) == 5]) + len([x for x in teleop_grid[1] if int(x) == 6])} - {len([x for x in teleop_grid[1] if int(x) == 2]) + len([x for x in teleop_grid[1] if int(x) == 5]) + len([x for x in teleop_grid[1] if int(x) == 4])*2 + len([x for x in teleop_grid[1] if int(x) == 7])}") # 3 -> two cones, 5 -> cone/cube, 4 -> two cubes, 7 -> cube, 6 -> cone
        team_d.append(f"{len([x for x in teleop_grid[0] if int(x) == 1]) + len([x for x in teleop_grid[0] if int(x) == 3])*2 + len([x for x in teleop_grid[0] if int(x) == 5]) + len([x for x in teleop_grid[0] if int(x) == 6])} - {len([x for x in teleop_grid[0] if int(x) == 2]) + len([x for x in teleop_grid[0] if int(x) == 5]) + len([x for x in teleop_grid[0] if int(x) == 4])*2 + len([x for x in teleop_grid[0] if int(x) == 7])}") # 3 -> two cones, 5 -> cone/cube, 4 -> two cubes, 7 -> cube, 6 -> cone
        team_d.append(m[6])
        team_d.append(m[7])
        team_d.append(m[8])
        team_d.append(m[9])
        team_d.append(m[10])
        team_d.append(m[11])
        team_d.append(m[12])
        data.append(team_d)
    pit = []
    pit = db.execute("SELECT * FROM pit_scouting_2023 WHERE team_number=:team AND comp_code=:comp", {"team": team, "comp": comp_code}).fetchall()
    

    if len(pit) == 0:
        pit = [["N/A" for i in range(12)]]

    return render_template("2023/team.html", matches=data, team=team, comps=comps, pit=pit, team_name=get_team_name(team))


@analysis_bp.route("/alliance/2023")
@login_required
def alliance_view():
    # data = get_match_schedule("test", 1, test=True)
    return render_template("2023/alliance.html", comps=comps)


@analysis_bp.route("/rankings/2022", methods=['GET', 'POST'])
@login_required
def rankings_list_2022():
    comp = request.args.get("code")
    if comp is None:
        all_teams = []
        dic_team_with_average = {}
    else:
        all_teams = get_teams_at_event(comp)
        team_with_selected_data_values = db.execute("""SELECT * FROM scouting WHERE team IN {teams} AND comp_code=:comp""".format(teams=all_teams), {
            "comp": comp
        }).fetchall()

        dic_team_with_average = dict(
            zip(all_teams, ([0] * 7 for team in range(len(all_teams)))))
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
                score_sum[score_index] = (
                    round(score_sum[score_index] / score_sum[-1], 2))
    return render_template("rankings.html", calculated_averages=dic_team_with_average, comps=comps)

@analysis_bp.route("/rankings", methods=['GET', 'POST'])
@login_required
def rankings_list_2023():
    if session.get("email") in PIT_SCOUT_EMAIL:
        return "Unauthorized. As a pit scout, you can only view the <a href='/analysis/team'>teams page</a> or submit <a href='/pit/scout/2023'>pit scouting data</a>"

    teamAverage = []
    comp = request.args.get("code")
    if comp is None:
        average = {}
    else:
        data = db.execute("SELECT * FROM scouting_2023 WHERE comp_code=:comp", {
            "comp": comp
        }).fetchall()

        unwanted_removed = {}
        average = {}

        for match in data:
            if match[11].lower() not in DNP:
                if unwanted_removed.get(match[1]) == None:
                    unwanted_removed[match[1]] = [match]
                else:
                    unwanted_removed[match[1]].append(match)

        for team_num in list(unwanted_removed.keys()):
            match_total = 0
            match_count = 0
            auto = 0
            teleop = 0
            auto_endgame = 0
            teleop_endgame = 0
            driver = 0
            defense = 0
            def_match = 0

            for match in unwanted_removed[team_num]:
                auto_grid_score = grid_score(json.loads(match[3]), auto=True)
                #print(auto_grid_score, team_num)
                teleop_grid_score = grid_score(json.loads(match[5]))

                if match[4] == 1:
                    auto += 3
                    match_total += 3
                elif match[4] == 2:
                    auto += 8
                    match_total += 8
                elif match[4] == 3:
                    auto += 12
                    match_total += 12

                if match[8] == 1:
                    teleop_endgame += 2
                    match_total += 2
                elif match[8] == 2:
                    teleop_endgame += 6
                    match_total += 6
                elif match[8] == 3:
                    teleop_endgame += 10
                    match_total += 10
                
                total_score = auto_grid_score + teleop_grid_score

                match_total += total_score
                match_count += 1
                auto += auto_grid_score
                teleop += teleop_grid_score
                driver += match[9]
                defense += match[10]
                
                if match[10] > 0:
                    def_match += 1

    
            if match_count == 0:
                match_count = 1
            if def_match == 0:
                def_match = 1

            average[team_num] = [round(match_total / match_count, 2), round(auto / match_count, 2), round(teleop / match_count, 2), round(teleop_endgame / match_count, 2), round(driver / match_count, 2), round(defense / def_match, 2)]

    return render_template("2023/rankings.html", calculated_averages=average, comps=comps)

@analysis_bp.route("/rankings/all", methods=['GET', 'POST'])
@login_required
def rankings_list_2023_all():
    if session.get("email") in PIT_SCOUT_EMAIL:
        return "Unauthorized. As a pit scout, you can only view the <a href='/analysis/team'>teams page</a> or submit <a href='/pit/scout/2023'>pit scouting data</a>"

    teamAverage = []
    comp = request.args.get("code")
    if comp is None:
        average = {}
    else:
        data = db.execute("SELECT * FROM scouting_2023 WHERE comp_code=:comp", {
            "comp": comp
        }).fetchall()

        data_sorted_by_team = {}
        average = {}

        for match in data:
            if data_sorted_by_team.get(match[1]) == None:
                data_sorted_by_team[match[1]] = [match]
            else:
                data_sorted_by_team[match[1]].append(match)

        for team_num in list(data_sorted_by_team.keys()):
            match_total = 0
            match_count = 0
            auto = 0
            teleop = 0
            # auto_endgame = 0
            teleop_endgame = 0
            driver = 0
            defense = 0

            for match in data_sorted_by_team[team_num]:
                auto_grid_score = grid_score(json.loads(match[3]), auto=True)
                teleop_grid_score = grid_score(json.loads(match[5]))
                # auto_endgame TBD
                
                if match[4] == 1:
                    auto += 3
                    match_total += 3
                elif match[4] == 2:
                    auto += 8
                    match_total += 8
                elif match[4] == 3:
                    auto += 12
                    match_total += 12

                if match[8] == 1:
                    teleop_endgame += 2
                    match_total += 2
                elif match[8] == 2:
                    teleop_endgame += 6
                    match_total += 6
                elif match[8] == 3:
                    teleop_endgame += 10
                    match_total += 10
                
                total_score = auto_grid_score + teleop_grid_score

                match_total += total_score
                match_count += 1
                auto += auto_grid_score
                teleop += teleop_grid_score
                driver += match[9]
                
                if match[10] > 0:
                    defense += match[10]

            if match_count == 0:
                match_count = 1
                        
            average[team_num] = [round(match_total / match_count, 2), round(auto / match_count, 2), round(teleop / match_count, 2), round(teleop_endgame / match_count, 2), round(driver / match_count, 2), round(defense / match_count, 2)]

    return render_template("2023/rankings.html", calculated_averages=average, comps=comps)

@analysis_bp.route("/api/get_match_schedule/<string:event_key>/<string:match_num>")
def api_get_match_schedule(event_key, match_num):
    # {"red": ["frc1", "frc2", "frc3"], "blue": ["frc4", "frc5", "frc6"]}
    teams_in_match = get_match_schedule(event_key, int(match_num))
    positions = ['red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']
    averages_for_teams_in_match = dict(zip(positions, fetch_sql_for_dashboard(list(pos.split(
        'frc')[1] for pos in teams_in_match['red'] + teams_in_match['blue']), event_key)))

    return jsonify(averages_for_teams_in_match)


@analysis_bp.route("/api/2023/get_match_schedule/<string:event_key>/<string:match_num>")
def api_get_match_schedule_2023(event_key, match_num):
    # data = get_match_schedule(event_key, match_num, test=True)
    data = get_match_schedule(event_key, match_num, test=False)

    red_1_data = team_data(int(data["red"][0].split("frc")[1]), event_key)
    red_2_data = team_data(int(data["red"][1].split("frc")[1]), event_key)
    red_3_data = team_data(int(data["red"][2].split("frc")[1]), event_key)

    blue_1_data = team_data(int(data["blue"][0].split("frc")[1]), event_key)
    blue_2_data = team_data(int(data["blue"][1].split("frc")[1]), event_key)
    blue_3_data = team_data(int(data["blue"][2].split("frc")[1]), event_key)

    result = {
        "red1": {
            "team_number": data["red"][0].split("frc")[1],
            "auto_balanced": red_1_data[0],
            "auto_score": red_1_data[1],
            "teleop_cone": red_1_data[2],
            "teleop_cube": red_1_data[3],
            "teleop_climb": red_1_data[4],
            "total_average": red_1_data[5],
        },
        "red2": {
            "team_number": data["red"][1].split("frc")[1],
            "auto_balanced": red_2_data[0],
            "auto_score": red_2_data[1],
            "teleop_cone": red_2_data[2],
            "teleop_cube": red_2_data[3],
            "teleop_climb": red_2_data[4],
            "total_average": red_2_data[5],
        },
        "red3": {
            "team_number": data["red"][2].split("frc")[1],
            "auto_balanced": red_3_data[0],
            "auto_score": red_3_data[1],
            "teleop_cone": red_3_data[2],
            "teleop_cube": red_3_data[3],
            "teleop_climb": red_3_data[4],
            "total_average": red_3_data[5],
        },
        "blue1": {
            "team_number": data["blue"][0].split("frc")[1],
            "auto_balanced": blue_1_data[0],
            "auto_score": blue_1_data[1],
            "teleop_cone": blue_1_data[2],
            "teleop_cube": blue_1_data[3],
            "teleop_climb": blue_1_data[4],
            "total_average": blue_1_data[5],
        },
        "blue2": {
            "team_number": data["blue"][1].split("frc")[1],
            "auto_balanced": blue_2_data[0],
            "auto_score": blue_2_data[1],
            "teleop_cone": blue_2_data[2],
            "teleop_cube": blue_2_data[3],
            "teleop_climb": blue_2_data[4],
            "total_average": blue_2_data[5],
        },
        "blue3": {
            "team_number": data["blue"][2].split("frc")[1],
            "auto_balanced": blue_3_data[0],
            "auto_score": blue_3_data[1],
            "teleop_cone": blue_3_data[2],
            "teleop_cube": blue_3_data[3],
            "teleop_climb": blue_3_data[4],
            "total_average": blue_3_data[5],
        },
    }
    return jsonify(result)


def fetch_sql_for_dashboard(teams, comp_code):

    teams = list(teams)

    # Madtown offseason bot lookup
    keys = MADTOWN_2022_OFFSEASON_BOTS.keys()
    for i in range(len(teams)):
        if teams[i] in keys:
            teams[i] = MADTOWN_2022_OFFSEASON_BOTS[teams[i]]
    teams = tuple(list(teams))

    matches_for_team = db.execute(
        '''SELECT * FROM scouting WHERE team IN {teams} AND "comp_code"=:comp'''.format(teams=teams), {"comp": comp_code}).fetchall()
    dic_matches_for_team = dict(
        zip(teams, ([int(teams[team])] + [0] * 7 for team in range(len(teams)))))

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
    # LOGAN DID THIS PART DONT BLAME ME IF YOU CANT UNDERSTAND IT !!!!!!
    all_averages = list()
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

    points_per_section.append(
        auto_cross_points + auto_upper_points + auto_lower_points)
    points_per_section.append(tele_upper_points + tele_lower_points)
    points_per_section.append(climb_points)
    points_per_section.append(sum(points_per_section))

    return points_per_section


@analysis_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def analysis_dashboard():
    if session.get("email") in PIT_SCOUT_EMAIL:
        return "Unauthorized. As a pit scout, you can only view the <a href='/analysis/team>'teams page</a> or submit <a href='/pit/scout/2023>'pit scouting data</a>"
    return render_template("2023/dashboard.html", comps=comps)
    # return redirect(f"/analysis/dashboard/{today.year}")
    # return render_template("error.html")
    # return render_template("dashboard.html", comps=comps)


@analysis_bp.route("/dashboard/2023", methods=['GET', 'POST'])
@login_required
def analysis_dashboard_2023():
    if session.get("email") in PIT_SCOUT_EMAIL:
        return "Unauthorized. As a pit scout, you can only view the <a href='/analysis/team>'teams page</a> or submit <a href='/pit/scout/2023>'pit scouting data</a>"
    # return render_template("error.html")
    return render_template("2023/dashboard.html", comps=comps)


@analysis_bp.route("/strikethrough")
def strikethrough():
    db.execute("INSERT INTO picklist (team, comp_code, strikethrough) VALUES (:t, :c, 'true')", {
        "t": request.args.get("team"),
        "c": request.args.get("comp")
    })
    db().commit()


@analysis_bp.route("/unstrikethrough")
def un_strikethrough():
    db.execute("DELETE FROM picklist WHERE team=:t AND comp_code=:comp", {
        "t": request.args.get("team"),
        "comp": request.args.get("comp")
    })
    db().commit()


@analysis_bp.route("/strikethrough-all")
def strikethrough_all():
    json_data = []
    results = db.execute("SELECT team FROM picklist WHERE comp_code=:comp", {
        "comp": request.args.get("comp")
    }).fetchall()

    for row in results:
        json_data.append(str(row[0]))

    return jsonify(json_data)


@analysis_bp.route("/get-offseason")
def get_offseason_bot():
    return jsonify(get_offseason_bots("2022mttd"))


@analysis_bp.route("/picklist")
def picklist_2023():
    comp = "2023cacc"

    if comp == None or comp == "testing":
        teams = []
    else:
        teams = sorted(get_teams_at_event(comp))


    data = c.execute("SELECT * FROM picklist WHERE comp=:comp", {
        "comp": comp
    }).fetchone()

    d = [[]]
    if data != None:
        d = json.loads(data[1])

    
    return render_template("2023/picklist.html", comps=comps, teams=teams, data=d)

@analysis_bp.route("/api/alliance/2023", methods=["GET", "POST"])
def alliance_2023_api():


    data = get_match_schedule(request.json["comp_code"], request.json["match_number"], test=True)


    red_1 = int(data["red"][0].split("frc")[1])
    red_2 = int(data["red"][1].split("frc")[1])
    red_3 = int(data["red"][2].split("frc")[1])

    blue_1 = int(data["blue"][0].split("frc")[1])
    blue_2 = int(data["blue"][1].split("frc")[1])
    blue_3 = int(data["blue"][2].split("frc")[1])

    red_nums = [red_1, red_2, red_3]
    blue_nums = [blue_1, blue_2, blue_3]


    data = fetch("SELECT team_number, auto_grid, tele_grid FROM scouting_2023 WHERE match_number=:match AND comp_code=:comp", {
        "match": request.json["match_number"],
        "comp": request.json["comp_code"],
    })

    # TODO: For some reason it returns config info instead acutal data
    red_auto = [[0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    #red_auto_config = [[None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None]]

    blue_auto = [[0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    #blue_auto_config = [[None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None]]

    red_teleop = [[0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    #red_teleop_config = [[None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None]]

    blue_teleop = [[0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    #blue_teleop_config = [[None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None]]

    for row in data:
        if row[0] in red_nums:
            for i in range(3):
                for j in range(9):
                    if red_auto[i][j] == 0 and json.loads(row[1])[i][j] != 0:
                        red_auto[i][j] = json.loads(row[1])[i][j]
                        #red_auto_config[i][j] = row[0]
                    if red_teleop[i][j] == 0 and json.loads(row[2])[i][j] != 0:
                        red_teleop[i][j] = json.loads(row[2])[i][j]
                        #red_teleop_config[i][j] = row[0]
    
    for row in data:
        if row[0] in blue_nums:
            for i in range(3):
                for j in range(9):
                    if blue_auto[i][j] == 0 and json.loads(row[1])[i][j] != 0:
                        blue_auto[i][j] = json.loads(row[1])[i][j]
                        #blue_auto_config[i][j] = row[0]
                    if blue_teleop[i][j] == 0 and json.loads(row[2])[i][j] != 0:
                        blue_teleop[i][j] = json.loads(row[2])[i][j]
                        #blue_teleop_config[i][j] = row[0]


    return jsonify({"red_auto": red_auto, "red_teleop": red_teleop, "blue_auto": blue_auto, "blue_teleop": blue_teleop}) #  "red_auto_config": red_auto_config, "blue_auto_config": blue_auto_config, "red_teleop_config": red_teleop_config, "blue_teleop_config": blue_teleop_config


def two_people(lst):
    """
    list will be sorted in this order: match 1, match 101, match 2, match 102, etc. 
    Assume the list is already sorted by match number asc
    """
    match_to_data = {}

    for row in lst:
        match_to_data[row[2]] = row

    new_data = []

    for row in lst:
        if row[2] <= 100:
            new_data.append(row)
            try:
                new_data.append(match_to_data[100 + row[2] % 100])
            except Exception as e:
                print("e")

        if row[2] > 200:
            new_data.append(match_to_data[row[2]])

        # if row[2] > 200 and row[2] < 300:
        #     new_data.append(match_to_data)
        #     try:
        #         new_data.append(match_to_data[200 + row[2] % 100])
        #     except Exception as e:
        #         print(e)

    return new_data

@analysis_bp.route("/api/2023/save", methods=["GET", "POST"])
def save_picklist_2023():
    comp = request.json["comp"]
    

    c.execute("DELETE FROM picklist WHERE comp=:comp", {
        "comp": comp
    })
    conn.commit()

    c.execute("INSERT INTO picklist (data, comp) VALUES (:data, :comp)", {
        "data": json.dumps(request.json),
        "comp": comp
    })
    conn.commit()

    return jsonify({"success": True})

@analysis_bp.route("/api/2023/picklist/fetch")
def fetch_picklist():
    comp = request.args.get("comp")
    
    data = c.execute("SELECT * FROM picklist WHERE comp=:comp", {
        "comp": comp
    }).fetchone()

    d = [[]]
    if data != None:
        d = json.loads(data[1])

    return jsonify(d)
