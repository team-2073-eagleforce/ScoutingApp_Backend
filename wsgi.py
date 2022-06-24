from scouting_backend import create_app

app = create_app()
app.config["SECRET_KEY"] = "Nishan_update"

if __name__ == "__main__":
    app.run(port=5003, debug=True)
