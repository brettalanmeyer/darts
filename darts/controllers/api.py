from darts import app
from flask import Response, render_template, redirect, request
from darts.entities import match as matchModel
from darts.entities import player as playerModel
from darts.entities import team as teamModel
from darts.entities import team_player as teamPlayerModel
from darts.entities import mark as markModel
from darts.entities import mode as modeModel
from darts import model
import json

@app.route("/api/", methods = ["GET"])
def api_index():
	return render_template("api/index.html")

@app.route("/api/players/", methods = ["GET"])
def api_players():
	players = model.Model().select(playerModel.Player)

	data = []

	for player in players:
		data.append({
			"id": player.id,
			"name": player.name,
			"createdAt": str(player.createdAt)
		})

	return json_response(data)

@app.route("/api/matches/", methods = ["GET"])
def api_matches():
	matches = model.Model().select(matchModel.Match)

	data = []

	for match in matches:
		data.append({
			"id": match.id,
			"players": match.players,
			"game": match.game,
			"round": match.round,
			"ready": toBoolean(match.ready),
			"turn": match.turn,
			"complete": toBoolean(match.complete),
			"createdAt": str(match.createdAt)
		})

	return json_response(data)

@app.route("/api/marks/", methods = ["GET"])
def api_marks():
	marks = model.Model().select(markModel.Mark)

	data = []

	for mark in marks:
		data.append({
			"id": mark.id,
			"matchId": mark.matchId,
			"teamId": mark.teamId,
			"playerId": mark.playerId,
			"game": mark.game,
			"round": mark.round,
			"value": mark.value,
			"createdAt": str(mark.createdAt)
		})

	return json_response(data)

@app.route("/api/teams/", methods = ["GET"])
def api_teams():
	teams = model.Model().select(teamModel.Team)

	data = []

	for team in teams:
		data.append({
			"id": team.id,
			"matchId": team.matchId,
			"win": toBoolean(team.win),
			"loss": toBoolean(team.loss)
		})

	return json_response(data)

@app.route("/api/teams-players/", methods = ["GET"])
def api_teams_players():
	teamPlayers = model.Model().select(teamPlayerModel.TeamPlayer)

	data = []

	for teamPlayer in teamPlayers:
		data.append({
			"id": teamPlayer.id,
			"teamId": teamPlayer.teamId,
			"playerId": teamPlayer.playerId
		})

	return json_response(data)

@app.route("/api/modes/", methods = ["GET"])
def api_modes():
	modes = model.Model().select(modeModel.Mode)

	data = []

	for mode in modes:
		data.append({
			"id": mode.id,
			"name": mode.name,
			"mode": mode.mode,
			"alias": mode.alias,
			"enabled": toBoolean(mode.enabled)
		})

	return json_response(data)

def json_response(data):
	return Response(json.dumps(data), status = 200, mimetype = "application/json")

def toBoolean(value):
	if(value == 1):
		return True
	else:
		return False

