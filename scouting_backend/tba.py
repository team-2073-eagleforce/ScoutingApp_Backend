import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql://" + os.getenv("DATABASE_URL").split("://")[1])
db = scoped_session(sessionmaker(bind=engine))
conn = db()

X_TBA_Auth_Key = os.getenv("TBA_AUTH_KEY")

def get_match_team(event_key):
    t = []

    if event_key != "2022cacc":
        res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/teams", headers={
            "X-TBA-Auth-Key": X_TBA_Auth_Key
        })
        j = res.json()
        for team in res.json():
            t.append(int(team["team_number"]))
    else:
        j = [
            {"team_number": 2288},
            {"team_number": 5430},
            {"team_number": 4698},
            {"team_number": 3598},
            {"team_number": 5274},
            {"team_number": 1662},
            {"team_number": 3189},
            {"team_number": 8016},
            {"team_number": 3257},
            {"team_number": 5458},
            {"team_number": 4643},
            {"team_number": 1628},
            {"team_number": 701},
            {"team_number": 6918},
            {"team_number": 3859},
            {"team_number": 5817},
            {"team_number": 2135},
            {"team_number": 841},
            {"team_number": 6662},
            {"team_number": 6884},
            {"team_number": 5940},
            {"team_number": 8048},
            {"team_number": 2643},
            {"team_number": 6059},
            {"team_number": 7777},
            {"team_number": 199},
            {"team_number": 5700},
            {"team_number": 1072},
            {"team_number": 114},
            {"team_number": 7419},
            {"team_number": 5924},
            {"team_number": 7528},
            {"team_number": 2551},
            {"team_number": 1671},
        ]

    data = db.execute("SELECT DISTINCT team FROM scouting WHERE comp_code=:comp", {"comp": event_key}).fetchall()
    print(data)
    for d in data:
        if d[0] not in t:
            #t.append(d)
            j.append({"team_number": d[0]})

    return (j)


def get_match_schedule(event_key, match_num):
    res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches", headers={
        "X-TBA-Auth-Key": X_TBA_Auth_Key  
    })
    
    # with open("data.json", "w") as f:
    #     f.write(str(res.json()))
    for r in res.json():
        if r["match_number"] == match_num:
            return {
                "red": r["alliances"]["red"]["team_keys"],
                "blue": r["alliances"]["blue"]["team_keys"]
            }
    return res.json()

def get_comps(team, year=None):
    res = requests.get(f"https://www.thebluealliance.com/api/v3/team/frc{team}/events/{year}", headers={
        "X-TBA-Auth-Key": X_TBA_Auth_Key
    })
    comps = {}

    for r in res.json():
        comps[r["key"]] = r["short_name"]
    
    comps["testing"] = "Demo/Training"
    return comps