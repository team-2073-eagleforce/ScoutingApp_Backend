from scouting_backend import create_app
# from sentry_sdk.integrations.flask import FlaskIntegration
# import sentry_sdk
import os
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception, request, session
from werkzeug.exceptions import InternalServerError
import traceback
import sendgrid
from scouting_backend.helpers import create_message
sg = sendgrid.SendGridAPIClient()


# sentry_sdk.init(
#     dsn=os.getenv("SENTRY_DSN"),
#     integrations=[
#         FlaskIntegration(),
#     ],

#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0
# )

app = create_app()
app.config["SECRET_KEY"] = "Nishan_update"

# @app.before_first_request
# def init_rollbar():
#     """init rollbar module"""
#     rollbar.init(
#         # access token
#         os.getenv("ROLLBAR_ACCESS_TOKEN"),
#         # environment name
#         'production',
#         # server root directory, makes tracebacks prettier
#         root=os.path.dirname(os.path.realpath(__file__)),
#         # flask already sets up logging
#         allow_logging_basic_config=False)

#     # send exceptions from `app` to rollbar, using flask's signal system.
#     got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

@app.errorhandler(Exception)
def handle_500(e):
    print("error")
    error_tb = traceback.format_exc()
    try:
        resp = sg.send(create_message(error_tb + str(session) + str(request)))
    except Exception as exc:
        print(exc)
    return app.finalize_request(e, from_error_handler=True)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
