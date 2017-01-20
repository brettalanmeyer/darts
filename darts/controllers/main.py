from darts import app
from flask import render_template, request
from darts import model
from sqlalchemy import text
from darts.entities import game as gameModel
from darts.controllers.modes import cricket

@app.route("/")
def main_index():
	return render_template("main/index.html")
