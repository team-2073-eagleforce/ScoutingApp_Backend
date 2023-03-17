from functools import wraps
from flask import request, redirect, url_for, session
from constants import DNP

import cloudinary
import cloudinary.uploader
import cloudinary.api

import os
from database import fetch
import json

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(session.get('email'))
        if session.get("email") is None:
            return redirect("/google/authorize")
        return f(*args, **kwargs)
    return decorated_function

def pit_scout_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email") is None:
            return redirect("/google/authorize")
        return f(*args, **kwargs)
    return decorated_function

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

def upload_image(file):
    r = cloudinary.uploader.upload(file)
    img_url = r["secure_url"]
    return img_url

def create_message(email_text):
    import sendgrid
    return sendgrid.helpers.mail.Mail(
        from_email=os.environ["FROM_EMAIL"],
        to_emails=os.environ["TO_EMAIL"],
        subject='SCOUTING APP V2 - unhandled exception occurred!',
        plain_text_content=email_text,
    )

def is_non_desirable_scouter(name):
    if name.lower() in DNP:
        return True
    return False

def remove_non_desirable_data(data):
    """
    Args: 
    - data: list filled with tuples; tuple[11] is the name.

    Returns:
    Same format like data except with all DNP scouts' data removed

    Extra Credit: if you can use is_non_desirable_scounter function effectively
    """
    new_data = []
    for i in data:
        if not is_non_desirable_scouter(i[11]):
            new_data.append(i)
    return new_data


def team_data(team_num, comp_code):
    data = fetch("SELECT * FROM scouting_2023 WHERE team_number=:team AND comp_code=:comp_code", {
        "team": team_num,
        "comp_code": comp_code
    })

    auto_balanced = 0
    auto_total = 0
    auto_score_total = 0
    auto_average = 0
    teleop_cone_total = 0
    teleop_cube_total = 0
    points_total = 0

    for match in data:
        if match[4] == 3:
            auto_balanced += 1
        
        if match[4] == 2 or match[4] == 3:
            auto_total += 1
        
        auto_grid = json.loads(match[3])
        auto_score_total += grid_score(auto_grid, auto=True)
        teleop_grid = json.loads(match[5])
        cone, cube = count_objects(teleop_grid)
        teleop_cone_total += cone
        teleop_cube_total += cube
        total = grid_score(auto_grid, auto=True) + grid_score(teleop_grid)

        if match[4] == 1:
            total += 8
        elif match[4] == 2:
            total += 12

        if match[8] == 1:
            total += 2
        elif match[8] == 2:
            total += 6
        elif match[8] == 3:
            total += 10
        
        points_total += total
    
    if len(data) == 0:
        data = ["N/A"]
    
    print(team_num, auto_score_total, len(data))
    return [[auto_balanced, auto_total], round(auto_score_total / len(data), 2), round(teleop_cone_total / len(data), 2), round(teleop_cube_total / len(data), 2), 0, round(points_total / len(data), 2)] # Missing endgame, insert it before the last ele

def grid_score(grid, auto=False):
    score = 0

    grid = json.loads(grid)


    if auto:
        score += grid[0].count(1) * 6
        score += grid[1].count(1) * 4
        score += grid[2].count(1) * 3
        score += grid[0].count(2) * 6
        score += grid[1].count(2) * 4
        score += grid[2].count(2) * 3
    else:
        score += grid[0].count(1) * 5
        score += grid[1].count(1) * 3
        score += grid[2].count(1) * 2
        score += grid[0].count(2) * 5
        score += grid[1].count(2) * 3
        score += grid[2].count(2) * 2

    return score

def count_objects(grid):
    cone = 0
    cube = 0
    
    grid = json.loads(grid)

    for row in range(3):
        for col in range(7):
            if grid[row][col] == 1:
                cone += 1
            elif grid[row][col] == 2:
                cube += 1
    
    return cone, cube


def endgame_score(num, auto=False):
    pass