from darts import app, model
from darts.entities import match as matchModel
from darts.entities import team as teamModel
from darts.entities import mode as modeModel
from darts.entities import mark as markModel
from darts.entities import player as playerModel
from darts.entities import team_player as teamPlayerModel
from flask import render_template, request, redirect, Response
from datetime import datetime
import json

@app.route("/matches/<int:id>/modes/x01/", methods = ["GET"])
def x01_index(id):
	match = model.Model().selectById(matchModel.Match, id)
	mode = model.Model().selectById(modeModel.Mode, match.modeId)
	return render_template("matches/modes/x01/num-players.html", match = match, mode = mode)

@app.route("/matches/<int:id>/modes/x01/num-players/", methods = ["POST"])
def x01_create_num_players(id):
	match = model.Model().selectById(matchModel.Match, id)
	model.Model().update(matchModel.Match, match.id, { "players": request.form["players"] })

	for i in range(0, int(request.form["players"])):
		newTeam = teamModel.Team(match.id)
		model.Model().create(newTeam)

	return redirect("/matches/%d/modes/x01/players/" % match.id)

@app.route("/matches/<int:id>/modes/x01/players/", methods = ["GET"])
def x01_players(id):
	match = model.Model().selectById(matchModel.Match, id)
	mode = model.Model().selectById(modeModel.Mode, match.modeId)
	teamPlayers = getTeamPlayersByMatchId(match.id)
	teams = model.Model().select(teamModel.Team).filter_by(matchId = match.id)
	players = model.Model().select(playerModel.Player).filter_by(enabled = 1).order_by(playerModel.Player.name)
	return render_template("matches/modes/x01/players.html", match = match, mode = mode, teams = teams, players = players, teamPlayers = teamPlayers)

@app.route("/matches/<int:id>/modes/x01/players/", methods = ["POST"])
def x01_players_create(id):
	teamPlayer = teamPlayerModel.TeamPlayer(request.form["teamId"], request.form["playerId"])
	model.Model().create(teamPlayer)
	return Response(json.dumps({ "id": int(teamPlayer.id) }), status = 200, mimetype = "application/json")

@app.route("/matches/<int:id>/modes/x01/players/redo/", methods = ["POST"])
def x01_players_redo(id):
	teamPlayers = getTeamPlayersByMatchId(id)

	for teamPlayer in teamPlayers:
		model.Model().delete(teamPlayerModel.TeamPlayer, teamPlayer.id)

	return redirect("/matches/%d/modes/x01/players/" % id)

@app.route("/matches/<int:id>/modes/x01/play/", methods = ["POST"])
def x01_play_create(id):
	team = model.Model().select(teamModel.Team).filter_by(matchId = id).first()
	teamPlayer = model.Model().select(teamPlayerModel.TeamPlayer).filter_by(teamId = team.id).first()
	match = model.Model().selectById(matchModel.Match, id)
	model.Model().update(matchModel.Match, match.id, { "ready": True, "turn": teamPlayer.playerId })
	return redirect("/matches/%d/modes/x01/play/" % id)

@app.route("/matches/<int:id>/modes/x01/play/", methods = ["GET"])
def x01_play(id):
	match = model.Model().selectById(matchModel.Match, id)
	mode = model.Model().selectById(modeModel.Mode, match.modeId)
	teamPlayers = getTeamPlayersByMatchId(match.id)
	teams = model.Model().select(teamModel.Team).filter_by(matchId = match.id)

	data = {
		"id": int(match.id),
		"game": match.game,
		"round": match.round,
		"players": match.players,
		"num-players": 0,
		"turn": match.turn,
		"complete": match.complete,
		"players": [],
		"mode": mode
	}

	for team in teams:
		players = model.Model().select(teamPlayerModel.TeamPlayer).filter_by(teamId = team.id)

		for player in players:

			user = model.Model().selectById(playerModel.Player, player.playerId)
			teamPlayer = teamPlayers.filter_by(playerId = user.id).one()
			marks = model.Model().select(markModel.Mark).filter_by(matchId = match.id, playerId = player.playerId)
			playerPoints = int(mode.mode)

			for mark in marks:
				playerPoints -= mark.value

			data["players"].append({
				"id": user.id,
				"name": user.name,
				"teamId": teamPlayer.teamId,
				"points": playerPoints
			})

	data["num-players"] = len(data["players"])

	return render_template("matches/modes/x01/board.html", data = data)

@app.route("/matches/<int:matchId>/modes/x01/teams/<int:teamId>/players/<int:playerId>/matches/<int:game>/rounds/<int:round>/marks/<int:mark>/", methods = ["POST"])
def x01_score(matchId, teamId, playerId, game, round, mark):

	model.Model().update(matchModel.Match, matchId, { "round": round })

	newMark = markModel.Mark()
	newMark.matchId = matchId
	newMark.teamId = teamId
	newMark.playerId = playerId
	newMark.game = game
	newMark.round = round
	newMark.value = int(mark)
	newMark.createdAt = datetime.now()

	model.Model().create(newMark)

	return Response(json.dumps({ "id": int(newMark.id) }), status = 200, mimetype = "application/json")

@app.route("/matches/<int:matchId>/modes/x01/players/<int:playerId>/turn/", methods = ["POST"])
def x01_turn(matchId, playerId):
	model.Model().update(matchModel.Match, matchId, { "turn": playerId })
	return Response(json.dumps({ "id": matchId }), status = 200, mimetype = "application/json")

@app.route("/matches/<int:matchId>/modes/x01/undo/", methods = ["POST"])
def x01_undo(matchId):
	marks = model.Model().select(markModel.Mark).filter_by(matchId = matchId).order_by(markModel.Mark.id.desc())

	if marks.count() > 0:
		mark = marks.first()
		model.Model().update(matchModel.Match, matchId, { "turn": mark.playerId })
		model.Model().delete(markModel.Mark, mark.id)
		return Response(json.dumps({  "matchId": matchId, "playerId": mark.playerId, "value": mark.value, "valid": True }), status = 200, mimetype = "application/json")

	return Response(json.dumps({ "id": matchId, "valid": False }), status = 200, mimetype = "application/json")

def getTeamPlayersByMatchId(matchId):
	teams = model.Model().select(teamModel.Team).filter_by(matchId = matchId)

	teamIds = []
	for team in teams:
		teamIds.append(team.id)

	teamPlayers = model.Model().select(teamPlayerModel.TeamPlayer).filter(teamPlayerModel.TeamPlayer.teamId.in_(teamIds)).order_by("id")

	return teamPlayers
