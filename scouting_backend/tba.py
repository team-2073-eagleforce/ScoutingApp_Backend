import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql://iovoclgutwvauo:96baff9ff4b4e43005ef48d270eea03a98ff3ab03a1917c35e853e92589bccc4@ec2-52-204-195-41.compute-1.amazonaws.com:5432/d2csu45r67sphs")
db = scoped_session(sessionmaker(bind=engine))

X_TBA_Auth_Key = "OfVisf5XygZ2368Z4ynIyVmYCUz2ktv4cJ7v3ttWyzIo4Uf3YnVnr21iDrY95rwj"

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
