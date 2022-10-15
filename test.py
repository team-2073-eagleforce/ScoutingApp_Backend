import requests
import json

res = requests.get(f"https://www.thebluealliance.com/api/v3/event/2017cacc/teams", headers={
    "X-TBA-Auth-Key": "c6VZpR2NvDFhm1ixTkaG3xmvY8iGCHKMGCEDtO7qGnCTaTeRfjGYn1WflqVUYYcZ"
})

with open('test.json', "w") as f:
    f.write(json.dumps(res.json()))