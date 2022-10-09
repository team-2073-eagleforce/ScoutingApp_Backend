import os
import requests

X_TBA_Auth_Key = os.getenv("TBA_AUTH_KEY")


def get_match_team(event_key):
    res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/teams", headers={
        "X-TBA-Auth-Key": X_TBA_Auth_Key
    })
    return (res.json())


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