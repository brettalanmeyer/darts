from darts import app, model
from darts.entities import match as matchModel
from darts.entities import player as playerModel
from darts.entities import team as teamModel
from darts.entities import team_player as teamPlayerModel
from darts.entities import mark as markModel
from darts.entities import result as resultModel
from darts.entities import mode as modeModel
from darts.entities import mark_style as markStyleModel
from flask import Response, render_template, redirect, request
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.sql.expression import func
import json, random

@app.route("/matches/<int:id>/modes/cricket/")
def cricket_index(id):
	return redirect("/matches/%d/modes/cricket/num-games/" % id)

@app.route("/matches/<int:id>/modes/cricket/num-games/")
def cricket_num_games(id):
	match = model.Model().selectById(matchModel.Match, id)
	return render_template("matches/modes/cricket/num-games.html", match = match)

@app.route("/matches/<int:id>/modes/cricket/num-games/", methods = ["POST"])
def cricket_num_games_create(id):
	match = model.Model().selectById(matchModel.Match, id)
	model.Model().update(matchModel.Match, match.id, { "games": request.form["games"] })
	return redirect("/matches/%d/modes/cricket/num-players/" % id)

@app.route("/matches/<int:id>/modes/cricket/num-players/")
def cricket_num_players(id):
	match = model.Model().selectById(matchModel.Match, id)
	return render_template("matches/modes/cricket/num-players.html", match = match)

@app.route("/matches/<int:id>/modes/cricket/num-players/", methods = ["POST"])
def cricket_create_num_players(id):
	match = model.Model().selectById(matchModel.Match, id)
	model.Model().update(matchModel.Match, match.id, { "players": request.form["players"] })

	for i in range(0, 2):
		newTeam = teamModel.Team(match.id)
		model.Model().create(newTeam)

	return redirect("/matches/%d/modes/cricket/players/" % match.id)

@app.route("/matches/<int:id>/modes/cricket/play/", methods = ["GET"])
def cricket_board(id):
	markStyles = get_mark_styles().order_by(func.rand())
	markStyle = markStyles.first()
	markStyleIds = []
	for ms in markStyles:
		markStyleIds.append(int(ms.id))
	return render_template("matches/modes/cricket/board.html", match = getGameData(id), markStyle = markStyle, markStyleIds = markStyleIds)

def getGameData(id):
	match = model.Model().selectById(matchModel.Match, id)
	mode = model.Model().selectById(modeModel.Mode, match.modeId)
	results = model.Model().select(resultModel.Result).filter_by(matchId = match.id)
	teams = model.Model().select(teamModel.Team).filter_by(matchId = match.id)

	data = {
		"id": int(match.id),
		"games": match.games,
		"game": match.game,
		"round": match.round,
		"players": match.players,
		"turn": match.turn,
		"teams": [],
		"results": [],
		"points": [20, 19, 18, 17, 16, 15],
		"complete": match.complete,
		"createdAt": str(match.createdAt).replace("-", "/")
	}

	if mode.mode == "random-crickets":
		data["points"] = map(int, match.data.split(","))

	for result in results:
		data["results"].append({
			"game": result.game,
			"teamId": result.teamId,
			"score": result.score,
			"win": result.win,
			"loss": result.loss
		})

	for team in teams:

		teamData = {
			"id": team.id,
			"players": [],
			"marks": {
				25: 0,
				"points": 0
			},
			"results": []
		}

		for i in range(0, 21):
			teamData["marks"][i] = 0

		print(teamData)

		for i in range(1, 6):
			results = model.Model().select(resultModel.Result).filter_by(matchId = match.id, teamId = team.id, game = i)
			resultSet = {
				"score": 0,
				"win": 0,
				"loss": 0
			}

			if results.count() > 0:
				result = results.first()
				resultSet["score"] = result.score
				resultSet["win"] = result.win
				resultSet["loss"] = result.loss

			teamData["results"].append(resultSet)

		players = model.Model().select(teamPlayerModel.TeamPlayer).filter_by(teamId = team.id)

		for player in players:

			user = model.Model().selectById(playerModel.Player, player.playerId)

			teamData["players"].append({
				"id": user.id,
				"name": user.name,
				"mpr": getMarksPerRound(match.id, player.playerId, None),
				"mpr1": getMarksPerRound(match.id, player.playerId, 1),
				"mpr2": getMarksPerRound(match.id, player.playerId, 2),
				"mpr3": getMarksPerRound(match.id, player.playerId, 3),
				"mpr4": getMarksPerRound(match.id, player.playerId, 4),
				"mpr5": getMarksPerRound(match.id, player.playerId, 5)
			})

		scored = {
			25: 0
		}

		for i in range(0, 21):
			scored[i] = 0

		pointsScored = 0

		marks = model.Model().select(markModel.Mark).filter_by(matchId = match.id, teamId = team.id, game = match.game)

		for mark in marks:
			teamData["marks"][mark.value] += 1
			scored[mark.value] += 1
			if scored[mark.value] > 3:
				pointsScored += mark.value

		teamData["marks"]["points"] = pointsScored

		data["teams"].append(teamData)

	return data

@app.route("/matches/<int:id>/modes/cricket/spectator/")
def cricket_spactator(id):
	return Response(json.dumps(getGameData(id)), status = 200, mimetype = "application/json")

@app.route("/matches/<int:id>/modes/cricket/randomize/", methods = ["POST"])
def cricket_randomize(id):
	teamPlayers = getTeamPlayersByGameId(id)
	playerIds = []

	for teamPlayer in teamPlayers:
		playerIds.append(teamPlayer.playerId)
	random.shuffle(playerIds)

	for i, teamPlayer in enumerate(teamPlayers):
		model.Model().update(teamPlayerModel.TeamPlayer, teamPlayer.id, { "playerId": playerIds[i] })

	return redirect("/matches/%d/modes/cricket/players/" % id)

@app.route("/matches/<int:id>/modes/cricket/play/", methods = ["POST"])
def cricket_play(id):
	team = model.Model().select(teamModel.Team).filter_by(matchId = id).first()
	teamPlayer = model.Model().select(teamPlayerModel.TeamPlayer).filter_by(teamId = team.id).first()
	match = model.Model().selectById(matchModel.Match, id)

	data = {
		"ready": True,
		"turn": teamPlayer.playerId
	}

	mode = model.Model().selectById(modeModel.Mode, match.modeId)
	if mode.mode == "random-crickets":
		values = []
		for i in range(1,21):
			values.append(i);
		random.shuffle(values)
		points = values[0:6]
		points.sort(reverse = True)
		data["data"] = ",".join(map(str, points))

	model.Model().update(matchModel.Match, match.id, data)
	return redirect("/matches/%d/modes/cricket/play/" % id)

@app.route("/matches/<int:id>/modes/cricket/players/", methods = ["GET"])
def cricket_players(id):
	match = model.Model().selectById(matchModel.Match, id)
	mode = model.Model().selectById(modeModel.Mode, match.modeId)
	teamPlayers = getTeamPlayersByGameId(match.id)
	teams = model.Model().select(teamModel.Team).filter_by(matchId = match.id)
	players = model.Model().select(playerModel.Player).order_by(playerModel.Player.name)
	return render_template("matches/modes/cricket/players.html", match = match, teams = teams, players = players, teamPlayers = teamPlayers)

@app.route("/matches/<int:id>/modes/cricket/players/", methods = ["POST"])
def cricket_players_create(id):
	teamPlayer = teamPlayerModel.TeamPlayer(request.form["teamId"], request.form["playerId"])
	model.Model().create(teamPlayer)
	return Response(json.dumps({ "id": int(teamPlayer.id) }), status = 200, mimetype = "application/json")

@app.route("/matches/<int:id>/modes/cricket/", methods = ["POST"])
def cricket_start(id):
	match = model.Model().selectById(matchModel.Match, id)

	team1Player1 = teamPlayerModel.TeamPlayer(newTeam1.id, request.form["team-1-player-1-id"])
	model.Model().create(team1Player1)

	team2Player1 = teamPlayerModel.TeamPlayer(newTeam2.id, request.form["team-2-player-1-id"])
	model.Model().create(team2Player1)

	if match.players == 4:
		team1Player2 = teamPlayerModel.TeamPlayer(newTeam1.id, request.form["team-1-player-2-id"])
		model.Model().create(team1Player2)

		team2Player2 = teamPlayerModel.TeamPlayer(newTeam2.id, request.form["team-2-player-2-id"])
		model.Model().create(team2Player2)

	return redirect("/matches/%d/modes/cricket/" % id)

@app.route("/matches/<int:id>/modes/cricket/players/redo/", methods = ["POST"])
def cricket_players_redo(id):
	teamPlayers = getTeamPlayersByGameId(id)

	for teamPlayer in teamPlayers:
		model.Model().delete(teamPlayerModel.TeamPlayer, teamPlayer.id)

	return redirect("/matches/%d/modes/cricket/players/" % id)

@app.route("/matches/<int:id>/modes/cricket/next/", methods = ["POST"])
def cricket_next(id):
	match = model.Model().selectById(matchModel.Match, id)

	if match.complete:
		return redirect("/")

	turn = cricket_get_turn(match)
	model.Model().update(matchModel.Match, match.id, { "game": match.game + 1, "round": 1, "turn": turn })

	return redirect("/matches/%d/modes/cricket/play/" % match.id)

@app.route("/matches/<int:matchId>/modes/cricket/teams/<int:teamId>/players/<int:playerId>/matches/<int:game>/rounds/<int:round>/marks/<int:mark>/", methods = ["POST"])
def cricket_score(matchId, teamId, playerId, game, round, mark):

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

	mpr = getMarksPerRound(matchId, playerId, None)
	mpr1 = getMarksPerRound(matchId, playerId, 1)
	mpr2 = getMarksPerRound(matchId, playerId, 2)
	mpr3 = getMarksPerRound(matchId, playerId, 3)
	mpr4 = getMarksPerRound(matchId, playerId, 4)
	mpr5 = getMarksPerRound(matchId, playerId, 5)

	return Response(json.dumps({ "id": int(newMark.id), "playerId": playerId, "mpr": mpr, "mpr1": mpr1, "mpr2": mpr2, "mpr3": mpr3, "mpr4": mpr4, "mpr5": mpr5 }), status = 200, mimetype = "application/json")

@app.route("/matches/<int:matchId>/modes/cricket/undo/", methods = ["POST"])
def cricket_undo(matchId):
	match = model.Model().selectById(matchModel.Match, matchId)
	marks = model.Model().select(markModel.Mark).filter_by(matchId = matchId).order_by(markModel.Mark.id.desc())

	if marks.count() > 0:
		mark = marks.first()

		redirect = False
		if match.game != mark.game:
			redirect = True
			results = model.Model().select(resultModel.Result).filter_by(matchId = matchId, game = mark.game)
			for result in results:
				model.Model().delete(resultModel.Result, result.id)

		model.Model().update(matchModel.Match, matchId, { "game": mark.game, "round": mark.round, "turn": mark.playerId })
		model.Model().delete(markModel.Mark, mark.id)
		return Response(json.dumps({  "matchId": matchId, "teamId": mark.teamId, "playerId": mark.playerId, "value": mark.value, "valid": True, "redirect": redirect }), status = 200, mimetype = "application/json")

	return Response(json.dumps({ "id": matchId, "valid": False }), status = 200, mimetype = "application/json")

@app.route("/matches/<int:matchId>/modes/cricket/players/<int:playerId>/turn/", methods = ["POST"])
def cricket_turn(matchId, playerId):
	model.Model().update(matchModel.Match, matchId, { "turn": playerId })
	return Response(json.dumps({ "id": matchId }), status = 200, mimetype = "application/json")

@app.route("/matches/<int:matchId>/modes/cricket/teams/<int:teamId>/game/<int:game>/score/<int:score>/win/", methods = ["POST"])
def cricket_win(matchId, teamId, game, score):
	return result(matchId, teamId, game, score, 1, 0)

@app.route("/matches/<int:matchId>/modes/cricket/teams/<int:teamId>/game/<int:game>/score/<int:score>/loss/", methods = ["POST"])
def cricket_loss(matchId, teamId, game, score):
	return result(matchId, teamId, game, score, 0, 1)

@app.route("/matches/<int:matchId>/modes/cricket/teams/<int:teamId>/win/", methods = ["POST"])
def cricket_gameWin(matchId, teamId):
	return gameResult(matchId, teamId, 1, 0)

@app.route("/matches/<int:matchId>/modes/cricket/teams/<int:teamId>/loss/", methods = ["POST"])
def cricket_gameLoss(matchId, teamId):
	return gameResult(matchId, teamId, 0, 1)

def result(matchId, teamId, game, score, win, loss):
	newResult = resultModel.Result(matchId, teamId, game, score, win, loss, datetime.now())
	model.Model().create(newResult)
	return Response(json.dumps({ "id": matchId }), status = 200, mimetype = "application/json")

def gameResult(matchId, teamId, win, loss):
	model.Model().update(teamModel.Team, teamId, { "win": win, "loss": loss })
	if win == 1:
		model.Model().update(matchModel.Match, matchId, { "complete": 1, "completedAt": datetime.now() })
	return Response(json.dumps({ "id": teamId }), status = 200, mimetype = "application/json")

def getTeamPlayersByGameId(matchId):
	teams = model.Model().select(teamModel.Team).filter_by(matchId = matchId)

	teamIds = []
	for team in teams:
		teamIds.append(team.id)

	teamPlayers = model.Model().select(teamPlayerModel.TeamPlayer).filter(teamPlayerModel.TeamPlayer.teamId.in_(teamIds)).order_by("id")

	return teamPlayers

def getMarksPerRound(matchId, playerId, game):

	query = "SELECT (\
		SELECT COUNT(*)\
		FROM marks m\
		WHERE 1 = 1\
			AND m.value != 0\
			AND m.matchId = :matchId\
			AND m.playerId = :playerId\
	"
	if game != None:
		query += "\
			AND m.game = :game\
		"

	query += "\
		) as marks,\
		( SELECT COUNT(playerId) \
			FROM (\
				SELECT r.playerId, r.matchId, r.teamId, r.game, r.round\
				FROM marks r\
				LEFT JOIN matches g on r.matchId = g.id\
				WHERE g.id = :matchId\
	"

	if game != None:
		query += "\
			AND r.game = :game\
		"

	query += "\
				GROUP BY r.playerId, r.matchId, r.teamId, r.round, r.game\
			) AS rounds\
			WHERE playerId = :playerId\
		) AS rounds\
	"

	session = model.Model().getSession()
	connection = session.connection()
	data = connection.execute(text(query), matchId = matchId, playerId = playerId, game = game).first()

	marksPerRound = 0
	if data.rounds > 0:
		marksPerRound = float(data.marks) / float(data.rounds)

	return "{:.2f}".format(marksPerRound)

@app.route("/matches/<int:id>/modes/cricket/again/", methods = ["POST"])
def cricket_again(id):
	match = model.Model().selectById(matchModel.Match, id)
	newMatch = matchModel.Match(match.modeId, match.players, request.form["games"], 1, 1, True, 0, datetime.now())
	model.Model().create(newMatch)

	playerIds = []

	teams = model.Model().select(teamModel.Team).filter_by(matchId = id)
	for team in teams:
		newTeam = teamModel.Team(newMatch.id)
		model.Model().create(newTeam)

		teamPlayers = model.Model().select(teamPlayerModel.TeamPlayer).filter_by(teamId = team.id)
		for teamPlayer in teamPlayers:
			newTeamPlayer = teamPlayerModel.TeamPlayer(newTeam.id, teamPlayer.playerId)
			model.Model().create(newTeamPlayer)
			playerIds.append(teamPlayer.playerId)

	model.Model().update(matchModel.Match, newMatch.id, { "turn": playerIds[0] })

	return redirect("/matches/%d/modes/cricket/play/" % newMatch.id)


@app.route("/matches/modes/cricket/styles.css", methods = ["GET"])
def cricket_styles():
	return Response(render_template("matches/modes/cricket/styles.css", markStyles = get_mark_styles()), status = 200, mimetype = "text/css")

def get_mark_styles():
	return model.Model().select(markStyleModel.MarkStyle).filter_by(approved = 1, confirmed = 1)

def cricket_get_turn(match):

	gameNum = match.game + 1

	if match.complete:
		return redirect("/")

	teamPlayers = getTeamPlayersByGameId(match.id)

	if match.players == 4:
		if gameNum == 5:
			turn = teamPlayers[0].playerId
		elif gameNum == 4:
			turn = teamPlayers[3].playerId
		elif gameNum == 3:
			turn = teamPlayers[1].playerId
		elif gameNum == 2:
			turn = teamPlayers[2].playerId
		elif gameNum == 1:
			turn = teamPlayers[0].playerId
	else:
		if gameNum == 2 or gameNum == 4:
			turn = teamPlayers[1].playerId
		else:
			turn = teamPlayers[0].playerId

	return turn
