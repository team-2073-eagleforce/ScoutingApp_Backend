from scouting_backend import create_app
# from sentry_sdk.integrations.flask import FlaskIntegration
# import sentry_sdk
# import os

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

if __name__ == "__main__":
    app.run(port=5001, debug=True)
