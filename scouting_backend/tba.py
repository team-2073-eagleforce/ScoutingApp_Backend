import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from constants import MADTOWN_2022_OFFSEASON_BOTS

engine = create_engine("postgresql://" + os.getenv("DATABASE_URL").split("://")[1])
db = scoped_session(sessionmaker(bind=engine))
conn = db()

X_TBA_Auth_Key = os.getenv("TBA_AUTH_KEY")
madtown_offseason_value = list(MADTOWN_2022_OFFSEASON_BOTS.values())

def get_match_team(event_key):
    t = []
    j = []

    if event_key != "testing":
        res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/teams", headers={
            "X-TBA-Auth-Key": X_TBA_Auth_Key
        })
        j = res.json()
        for team in res.json():
            t.append(int(team["team_number"]))

    data = db.execute("SELECT DISTINCT team FROM scouting WHERE comp_code=:comp", {"comp": event_key}).fetchall()
    print(data)
    for d in data:
        if d[0] not in t:
            #t.append(d)
            j.append({"team_number": d[0]})
    
    if event_key == "2022mttd":
        for bot in madtown_offseason_value:
            if {"team_number": str(bot)} not in j:
                j.append({"team_number": bot})
    return (j)


def get_match_schedule(event_key, match_num, test=False):
    if test:
        print("hello")
        res = requests.get(f"https://tba-mock-2073.free.beeceptor.com/event/test/matches")
    else:
        print("world")
        res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches", headers={
            "X-TBA-Auth-Key": X_TBA_Auth_Key  
        })
    
    print(res.json())
    for r in res.json():
        if r["match_number"] == int(match_num):
            red = r["alliances"]["red"]["team_keys"]
            blue = r["alliances"]["blue"]["team_keys"]

            # for i in red:
            #     if i.split("frc")[1] in madtown_offseason_value:
            #         red = list(map(lambda x: x.replace(i, MADTOWN_2022_OFFSEASON_BOTS[i.split("frc")[1]]), red))

            # for i in red:
            #     if i.split("frc")[1] in madtown_offseason_value:
            #         red = list(map(lambda x: x.replace(i, MADTOWN_2022_OFFSEASON_BOTS[i.split("frc")[1]]), blue))
                
            return {
                "red": red,
                "blue": blue
            }
    return res.json()

def get_comps(team, year=None):
    res = requests.get(f"https://www.thebluealliance.com/api/v3/team/frc{team}/events/{year}", headers={
        "X-TBA-Auth-Key": X_TBA_Auth_Key
    })
    comps = {}

    for r in res.json():
        comps[r["key"]] = r["short_name"]
    
    comps["test"] = "Demo/Training"
    #comps["2022cacc"] = "CCC"
    #comps["2022mttd"] = "Madtown Throwdown"
    return comps

def get_offseason_bots(event_key):
    res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches", headers={
        "X-TBA-Auth-Key": X_TBA_Auth_Key  
    })
    
    # with open("data.json", "w") as f:
    #     f.write(str(res.json()))
    off_season_bots = []
    print(res.json())
    for r in res.json():
    
        red = r["alliances"]["red"]["team_keys"]
        blue = r["alliances"]["blue"]["team_keys"]

        for i in red:
            if not i.split("frc")[1].isnumeric():
                off_season_bots.append(i)
        
        for i in blue:
            if not i.split("frc")[1].isnumeric():
                off_season_bots.append(i)

    return sorted(set(off_season_bots))
