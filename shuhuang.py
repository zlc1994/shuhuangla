from application import app, db, migrate


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")