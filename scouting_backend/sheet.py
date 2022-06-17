import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient import discovery

SPREADSHEET_ID = '1cb7u43r9qbQg_tKyF8XVTSyu6CxLUnQPwCCTI1JAzCQ'

def edit_sheet(session, cell, data):
    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

    service = discovery.build('sheets', 'v4', credentials=credentials)
  
  # The spreadsheet to request.
    spreadsheet_id = '1cb7u43r9qbQg_tKyF8XVTSyu6CxLUnQPwCCTI1JAzCQ'  # TODO: Update placeholder value.
  
  # The A1 notation of the values to retrieve.
    range_ = cell 
  
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
                data
            ]
        ]
    }
  
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

    return response

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def sheet_properties(title, **sheet_properties):
  default_properties = {
    "properties": {
      "title": title,
      "index": 0,
      "sheetType": "GRID",
      "hidden": False
    }
  }
  return default_properties

def create_new_sheet(session, titles):
  credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

  service = discovery.build('sheets', 'v4', credentials=credentials)

  spreadsheet_id = '1txlnryg_Ic4uWbTXTlOlsTOs_edt9Md3XzCzIuvDhCA'  # TODO: Update placeholder value.
  requests = []

  for t in titles:
    requests.append({
      "addSheet": sheet_properties(t)
    })

  batch_update_values_request_body = {
    'requests': requests
  }

  request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_values_request_body).execute()
  response = request

  # TODO: Change code below to process the `response` dict:
  return response

def get_all_sheets(session):
  credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])
  sheets_name = []

  service = discovery.build('sheets', 'v4', credentials=credentials)
  sheets_meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
  sheets = sheets_meta.get("sheets", "")

  for s in sheets:
    sheets_name.append(s["title"])

  return sheets_name
