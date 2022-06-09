from flask import jsonify, render_template, Blueprint, request, session, redirect, url_for
from sqlalchemy import create_engine
from retrieval.models import matchEntry
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import os

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient import discovery

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

client_config = {
  "web": {
    "client_id": "351274848173-0eepc6g5hc4ri03l67rql056p7e6g8nv.apps.googleusercontent.com",
    "project_id": "scouting-excel-test",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
    "redirect_uris": [
      "https://google-sheet-interaction.boyuan12.repl.co/oauth2callback",
      "http://google-sheet-interaction.boyuan12.repl.co/oauth2callback",
      "https://team2073-scouting.herokuapp.com/oauth2callback",
      "http://team2073-scouting.herokuapp.com",
      "http://127.0.0.1:5001/oauth2callback"
    ],
    "javascript_origins": [
      "https://google-sheet-interaction.boyuan12.repl.co",
      "https://team2073-scouting.herokuapp.com",
      "http://127.0.0.1:5001"
    ]
  }
}

analysis_bp = Blueprint(
    'analysis_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
db = scoped_session(sessionmaker(bind=engine))
conn = db()

@analysis_bp.route("/matchSchedule", methods=["GET", "POST"])
def matchSchedule():
    return render_template("matchSchedule.html")

@analysis_bp.route("/team/<int:team>", methods=["GET"])
def view_team_data(team):
    results = db.execute("SELECT * FROM scouting WHERE team=:team", {"team": team})
    for r in results:
        print(r)
    return "LOL"

@analysis_bp.route("/sheet")
def google_sheet_rendering():
    return render_template("sheet.html")

@analysis_bp.route("/edit-sheet")
def edit_sheet():
    """
    range_: cell we want to modify
    value_range_body = {
        "values": [
            [
                "value to update"
            ]
        ]
    }
    """
    if 'credentials' not in session:
        return redirect('authorize')

  # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

    service = discovery.build('sheets', 'v4', credentials=credentials)
  
  # The spreadsheet to request.
    spreadsheet_id = '1cb7u43r9qbQg_tKyF8XVTSyu6CxLUnQPwCCTI1JAzCQ'  # TODO: Update placeholder value.
  
  # The A1 notation of the values to retrieve.
    range_ = 'B1'  # TODO: Update placeholder value.
  
  # How values should be represented in the output.
  # The default render option is ValueRenderOption.FORMATTED_VALUE.
    value_render_option = 'FORMATTED_VALUE'  # TODO: Update placeholder value. "['FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA']"
  
  # How dates, times, and durations should be represented in the output.
  # This is ignored if value_render_option is
  # FORMATTED_VALUE.
  # The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
    date_time_render_option = 'SERIAL_NUMBER'  # TODO: Update placeholder value.
  
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
    response = request.execute()
  
  # TODO: Change code below to process the `response` dict:
  # pprint(response)

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(credentials)

    # The ID of the spreadsheet to update.
  
  # The A1 notation of the values to update.
  
  # How the input data should be interpreted.
    value_input_option = 'RAW'  # TODO: Update placeholder value.
  
    value_range_body = {
        "values": [
            [
                "check"
            ]
        ]
    }
  
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()
  
  # TODO: Change code below to process the `response` dict:
  # pprint(response)

    return jsonify(**response)

@analysis_bp.route("/authorize")
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES)
    
    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('analysis_bp.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)

@analysis_bp.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('analysis_bp.oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    print(credentials_to_dict(credentials))
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('analysis_bp.google_sheet_rendering'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}
