from darts import app
from flask import render_template, request

@app.route("/")
def main_index():
	return render_template("main/index.html")

@app.route("/test/")
def main_test():
	return render_template("main/test.html")