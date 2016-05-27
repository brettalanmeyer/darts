import os
from flask import Flask, request, render_template
from flask.ext.assets import Environment, Bundle
from flask_mail import Mail

app = Flask(__name__)
assets = Environment(app)

app.config["MAIL_SERVER"] = ""
app.config["MAIL_PORT"] = ""
app.config["MAIL_USE_SSL"] = ""
app.config["MAIL_USERNAME"] = ""
app.config["MAIL_PASSWORD"] = ""

app.config.from_pyfile("config_mail.cfg")

mail = Mail(app)

from darts.controllers import api
from darts.controllers import brackets
from darts.controllers import matches
from darts.controllers import leaderboard
from darts.controllers import main
from darts.controllers import players
from darts.controllers import mark_styles

from darts.controllers.modes import cricket
from darts.controllers.modes import x01
from darts.controllers.modes import around_the_world

@app.errorhandler(404)
def not_found(error):
    return render_template("main/404.html"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("main/500.html"), 500

@app.after_request
def afterRequest(response):
	model.Model().close()
	return response

if __name__ == "__main__":
	app.run()
