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

    return (j)


def get_match_schedule(event_key, match_num):
    res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches", headers={
        "X-TBA-Auth-Key": X_TBA_Auth_Key  
    })
    
    # with open("data.json", "w") as f:
    #     f.write(str(res.json()))
    for r in res.json():
        if r["match_number"] == match_num:
            red = r["alliances"]["red"]["team_keys"]
            blue = r["alliances"]["blue"]["team_keys"]

            if "2073B" in red:
                red = list(map(lambda x: x.replace('frc2073B', 'frc9973'), red))
            if "2073B" in blue:
                blue = list(map(lambda x: x.replace('frc2073B', 'frc9973'), blue))

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
    
    comps["testing"] = "Demo/Training"
    comps["2022cacc"] = "CCC"
    return comps