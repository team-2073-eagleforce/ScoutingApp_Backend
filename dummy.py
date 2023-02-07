import random
import json
from database import load_json

def generate_grid(grid=None):
    top_row = []
    middle_row = []
    bottom_row = []
    a = 0
    b = 0

    for i in range(9):
        shape = 1
        if i == 1 or i == 4 or i == 7:
            shape = 2

        # if grid != None and grid[0][i] == 0:
        #     if random.random() > 0.5:
        #         top_row.append(shape)
        #     else:
        #         top_row.append(0)
        # elif grid != None and grid[0][i] != 0:
        #     top_row.append(0)

        if grid == None:
            if random.random() > 0.3:
                top_row.append(shape)
            else:
                top_row.append(0)
        
        
    for i in range(9):
        shape = 1
        if i == 1 or i == 4 or i == 7:
            shape = 2
        
        # if grid != None and grid[1][i] == 0:
        #     if random.random() > 0.5:
        #         middle_row.append(shape)
        #     else:
        #         middle_row.append(0)
        # elif grid != None and grid[1][i] != 0:
        #     middle_row.append(0)
        
        if grid == None:
            if random.random() > 0.3:
                middle_row.append(shape)
            else:
                middle_row.append(0)
        
            
    for i in range(9):
        # if grid != None and grid[2][i] == 0:
        #     res = random.random()
        #     if res < 0.33:
        #         bottom_row.append(0)
        #     elif res < 0.66:
        #         bottom_row.append(1)
        #     else:
        #         bottom_row.append(2)
        # elif grid != None and grid[2][i] != 0:
        #     bottom_row.append(0)
        
        if grid == None:
            res = random.random()
            if res < 0.2:
                bottom_row.append(0)
            elif res < 0.65:
                bottom_row.append(1)
            else:
                bottom_row.append(2)
    
    return [top_row, middle_row, bottom_row]


def generate_match_schedule():
    schedule = []
    for i in range(70):
        schedule.append([[], []])
        for j in range(3):
            schedule[i][0].append(random.randint(1, 40))
        for j in range(3):
            schedule[i][1].append(random.randint(1, 40))
    print(schedule)

    return schedule

def store_dummy_data(team, match_num):
    alliance = generate_grid()

    team_a_auto = [[], [], []]
    team_a_tele = [[], [], []]

    team_b_auto = [[], [], []]
    team_b_tele = [[], [], []]

    team_c_auto = [[], [], []]
    team_c_tele = [[], [], []]

    for i in range(3):
        for row in range(3):
            for j in range(9):
                if random.random() > 0.8 and alliance[row][j] != 0:
                    if i == 0:
                        team_a_auto[row].append(alliance[row][j])
                    elif i == 1:
                        team_b_auto[row].append(alliance[row][j])
                    elif i == 2:
                        team_c_auto[row].append(alliance[row][j])
                    alliance[row][j] = 0
                else:
                    if i == 0:
                        team_a_auto[row].append(0)
                    elif i == 1:
                        team_b_auto[row].append(0)
                    elif i == 2:
                        team_c_auto[row].append(0)
                
    print(team_a_auto)
    print(team_b_auto)
    print(team_c_auto)
    print("NEW: ", alliance)

    for row in range(3):
        for j in range(9):
            a_b_c = random.randint(0, 2)

            while True:
                if a_b_c == 0:
                    if len(team_a_tele[row]) < 9:
                        break
                elif a_b_c == 1:
                    if len(team_b_tele[row]) < 9:
                        break
                else:
                    if len(team_c_tele[row]) < 9:
                        break
                a_b_c = random.randint(0, 2)


            if a_b_c == 0:
                team_a_tele[row].append(alliance[row][j])
                team_b_tele[row].append(0)
                team_c_tele[row].append(0)

            elif a_b_c == 1:
                team_b_tele[row].append(alliance[row][j])
                team_a_tele[row].append(0)
                team_c_tele[row].append(0)

            elif a_b_c == 2:
                team_c_tele[row].append(alliance[row][j])
                team_a_tele[row].append(0)
                team_b_tele[row].append(0)

            alliance[row][j] = 0

    def transport_count(data):
        cone_count = 0
        cube_count = 0

        for i in range(3):
            for j in range(9):
                if data[i][j] == 1:
                    cone_count += 1
                if data[i][j] == 2:
                    cube_count += 1
        
        return random.randint(0, cone_count), random.randint(0, cube_count)


    # print(team_a_tele)
    # print(team_b_tele)
    # print(team_c_tele)

    team_a_overall = [[], [], []]
    team_b_overall = [[], [], []]
    team_c_overall = [[], [], []]

    for i in range(3):
        for j in range(9):
            team_a_overall[i].append(team_a_auto[i][j])

    for i in range(3):
        for j in range(9):
            if team_a_overall[i][j] != 0:
                team_a_overall[i][j] = team_a_auto[i][j]

    for i in range(3):
        for j in range(9):
            team_b_overall[i].append(team_b_auto[i][j])

    for i in range(3):
        for j in range(9):
            if team_b_overall[i][j] != 0:
                team_b_overall[i][j] = team_b_auto[i][j]

    for i in range(3):
        for j in range(9):
            team_c_overall[i].append(team_c_auto[i][j])

    for i in range(3):
        for j in range(9):
            if team_c_overall[i][j] != 0:
                team_c_overall[i][j] = team_c_auto[i][j]

    cone_transport_a, cube_transport_a = transport_count(team_a_overall)
    cone_transport_b, cube_transport_b = transport_count(team_b_overall)
    cone_transport_c, cube_transport_c = transport_count(team_c_overall)

    load_json({
        "team_number": team[0],
        "match_number": match_num,
        "auto_grid": team_a_auto,
        "tele_grid": team_a_tele,
        "auto_charging_station": random.randint(0, 2),
        "cone_transport": cone_transport_a,
        "cube_transport": cube_transport_a,
        "end_charging_station": random.randint(0, 3),
        "driver_ranking": random.randint(0, 5),
        "defense_ranking": random.randint(0, 5),
        "name": "John Doe",
        "comment": "test1",
        "comp_code": "test"
    })

    load_json({
        "team_number": team[1],
        "match_number": match_num,
        "auto_grid": team_b_auto,
        "tele_grid": team_b_tele,
        "auto_charging_station": random.randint(0, 2),
        "cone_transport": cone_transport_b,
        "cube_transport": cube_transport_b,
        "end_charging_station": random.randint(0, 3),
        "driver_ranking": random.randint(0, 5),
        "defense_ranking": random.randint(0, 5),
        "name": "Logan W.",
        "comment": "test2",
        "comp_code": "test"
    })

    load_json({
        "team_number": team[2],
        "match_number": match_num,
        "auto_grid": team_c_auto,
        "tele_grid": team_c_tele,
        "auto_charging_station": random.randint(0, 2),
        "cone_transport": cone_transport_c,
        "cube_transport": cube_transport_c,
        "end_charging_station": random.randint(0, 3),
        "driver_ranking": random.randint(0, 5),
        "defense_ranking": random.randint(0, 5),
        "name": "Mary",
        "comment": "test3",
        "comp_code": "test"
    })



def main():
    schedule_formatted = []
    schedule = generate_match_schedule() #[[[], []]]
    for match_num in range(len(schedule)):
        store_dummy_data(schedule[match_num][0], match_num+1)
        store_dummy_data(schedule[match_num][1], match_num+1)
    
    for match_num in range(len(schedule)):
        schedule_formatted.append({
            "alliances": {
            "blue": {
                "team_keys": [
                    f"frc{schedule[match_num][0][0]}",
                    f"frc{schedule[match_num][0][1]}",
                    f"frc{schedule[match_num][0][2]}",
                ]
            },
            "red": {
                "team_keys": [
                    f"frc{schedule[match_num][1][0]}",
                    f"frc{schedule[match_num][1][1]}",
                    f"frc{schedule[match_num][1][2]}",
                ]
            }
            },
            "match_number": match_num+1
        })

    with open("schedule.json", "w") as f:
        f.write(json.dumps(schedule_formatted))

main()

