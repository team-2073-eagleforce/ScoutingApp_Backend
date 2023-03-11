from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import json, os

engine = create_engine("postgresql://" + os.getenv("DATABASE_URL").split("://")[1])
db = scoped_session(sessionmaker(bind=engine))
conn = db()
c = conn

def load_json(data):
    """Summary or Description of the Function 
    Parameters: 
    data (dict): scouting data formatted as json (look at dummy folder for template)
    
    Returns: 
    None """
    team_number = data["teamNumber"]
    match_number = data["matchNumber"]
    auto_grid = json.dumps(data["autoGrid"])
    tele_grid = json.dumps(data["teleGrid"])
    auto_charging_station = data["autoChargingStation"]
    cone_transport = data["coneTransport"]
    cube_transport = data["cubeTransport"]
    end_charging_station = data["endChargingStation"]
    driver_ranking = data["driverRanking"]
    defense_ranking = data["defenseRanking"]
    name = data["name"]
    comment = data["comment"]
    comp_code = data["compCode"]

    results = c.execute("SELECT * FROM scouting_2023 WHERE team_number=:team AND match_number=:match AND comp_code=:comp AND name=:name", {
        "team": team_number,
        "match": match_number,
        "comp": comp_code,
        "name": name
    }).fetchall()

    if len(results) == 0:
        c.execute("INSERT INTO scouting_2023 (team_number, match_number, auto_grid, tele_grid, auto_charging_station, cone_transport, cube_transport, end_charging_station, driver_ranking, defense_ranking, name, comment, comp_code) VALUES (:team, :match, :ag, :tg, :auto_cs, :cone, :cube, :end_cs, :driver, :defense, :name, :comment, :comp_code)", {
            "team": team_number,
            "match": match_number,
            "ag": auto_grid,
            "tg": tele_grid,
            "auto_cs": auto_charging_station,
            "cone": cone_transport,
            "cube": cube_transport,
            "end_cs": end_charging_station,
            "driver": driver_ranking,
            "defense": defense_ranking,
            "name": name,
            "comment": comment,
            "comp_code": comp_code
        })
        conn.commit()


def fetch(sql_statement, params):
    return c.execute(sql_statement, params).fetchall()
