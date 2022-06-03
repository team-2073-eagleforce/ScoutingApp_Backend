
# EagleForce Scouting Server




## Environment Variables 

Create a file named .env and add the following variables directly under the ScoutingApp_Backend Directory. 

- ```FLASK_APP```=Entry point of your application; should be wsgi.py.
- ```FLASK_ENV```=The environment in which to run your application; either development or production.
- ```SECRET_KEY```=Randomly generated string of characters used to encrypt your app's data.
- ```SQLALCHEMY_DATABASE_URI```=mysql+pymysql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE_NAME]
- ```ASSETS_DEBUG (optional)```=False

_Remember never to commit secrets saved in .env files to Github._
## Installing Dependencies 

Run ```pip install -r requirements.txt``` to install dependencies