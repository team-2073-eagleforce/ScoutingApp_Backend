import requests

X_TBA_Auth_Key = "OfVisf5XygZ2368Z4ynIyVmYCUz2ktv4cJ7v3ttWyzIo4Uf3YnVnr21iDrY95rwj"

def get_match_team(event_key):
    res = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/teams", headers={
        "X-TBA-Auth-Key": X_TBA_Auth_Key
    })
    return (res.json())


