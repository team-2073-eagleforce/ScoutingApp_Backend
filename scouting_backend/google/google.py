import os

import google_auth_oauthlib.flow
import requests
from flask import jsonify, render_template, Blueprint, request, session, redirect, url_for

from scouting_backend import sheet
from scouting_backend.constants import AUTHORIZED_EMAIL, PIT_SCOUT_EMAIL
from scouting_backend.helpers import login_required

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

google_bp = Blueprint(
    'google_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email']

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
            "https://team2073-scouting.herokuapp.com/analysis/oauth2callback",
            "http://team2073-scouting.herokuapp.com",
            "http://127.0.0.1:5001/analysis/oauth2callback",
            "https://team2073-scouting.herokuapp.com/google/oauth2callback",
        ],
        "javascript_origins": [
            "https://google-sheet-interaction.boyuan12.repl.co",
            "https://team2073-scouting.herokuapp.com",
            "http://127.0.0.1:5001"
        ]
    }
}


@login_required
@google_bp.route("/sheet")
def google_sheet_rendering():
    return render_template("sheet.html")


@login_required
@google_bp.route("/edit-sheet")
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

    response = sheet.edit_sheet(session, "Sheet1!B5", "Hello World")

    return jsonify(**response)


@google_bp.route("/authorize")
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('google_bp.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    # session['state'] = state

    return redirect(authorization_url)


@google_bp.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify in the authorization server response.
    #state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES) # , state=state
    flow.redirect_uri = url_for('google_bp.oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    cred = credentials_to_dict(credentials)
    session['credentials'] = cred

    r = requests.get(f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={cred["token"]}').json()

    print(r)

    session["name"] = r["given_name"] + " " + r["family_name"]

    if r["email"] not in AUTHORIZED_EMAIL and r["email"] not in PIT_SCOUT_EMAIL:
        return "405 UNAUTHORIZED"

    session["email"] = r["email"]

    return redirect('/')


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
