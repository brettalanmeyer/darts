from darts import app
from flask import Response, render_template, redirect, request
from darts.entities import match as matchModel
from darts.entities import player as playerModel
from darts.entities import team as teamModel
from darts.entities import team_player as teamPlayerModel
from darts.entities import mark as markModel
from darts.entities import setting as settingModel
from darts.entities import mode as modeModel
from darts import model
from sqlalchemy import text
from datetime import datetime, timedelta

@app.route("/leaderboard/<path:modeName>/", methods = ["GET"])
def leaderboard_index(modeName):

	mode = model.Model().select(modeModel.Mode).filter_by(mode = modeName).first()

	modeId = str(mode.id)

	start = request.args.get("start")
	end = request.args.get("end")

	useStart = start is not None and len(start) > 0
	useEnd = end is not None and len(end) > 0

	startFormatted = ""
	endFormatted = ""

	if not useStart:
		startDate = model.Model().selectById(settingModel.Setting, 1).startDate
		if startDate != None:
			useStart = True
			start = startDate
			startFormatted = "{:%Y-%m-%d}".format(startDate)

	if not useEnd:
		endDate = model.Model().selectById(settingModel.Setting, 1).endDate
		if endDate != None:
			useEnd = True
			end = endDate
			endFormatted = "{:%Y-%m-%d}".format(endDate)

	if useEnd:
		date = datetime.strptime(str(end), "%Y-%m-%d %H:%M:%S").date()
		end = date + timedelta(days = 1)

	query = "\
		SELECT\
			p.id,\
			p.name,\
			(\
				SELECT COUNT(*)\
				FROM teams_players tp\
				LEFT JOIN teams t ON tp.teamId = t.id\
				LEFT JOIN matches g on t.matchId = g.id\
				WHERE tp.playerId = p.id AND g.modeId = :modeId  AND g.complete = 1\
	"

	if useStart:
		query += "\
			AND g.createdAt >= :start\
		"
	if useEnd:
		query += "\
			AND g.createdAt < :end\
		"

	query += "\
			) AS games,\
			(\
				SELECT COUNT(*)\
				FROM marks m\
				LEFT JOIN matches g on m.matchId = g.id\
				WHERE 1 = 1\
					AND m.playerId = p.id\
					AND m.value != 0\
					AND g.modeId = :modeId \
					AND g.complete = 1\
	"

	if useStart:
		query += "\
			AND g.createdAt >= :start\
		"
	if useEnd:
		query += "\
			AND g.createdAt < :end\
		"

	query += "\
			) AS marks,\
			(\
				SELECT COUNT(playerId) \
				FROM (\
					SELECT r.playerId, r.matchId, r.teamId, r.game, r.round\
					FROM marks r\
					LEFT JOIN matches g on r.matchId = g.id\
					WHERE g.modeId = :modeId  AND g.complete = 1\
	"

	if useStart:
		query += "\
			AND g.createdAt >= :start\
		"
	if useEnd:
		query += "\
			AND g.createdAt < :end\
		"

	query += "\
					GROUP BY r.playerId, r.matchId, r.teamId, r.round, r.game\
				) AS rounds\
				WHERE playerId = p.id\
			) AS rounds,\
			(\
				SELECT COUNT(*)\
				FROM players p2\
				LEFT JOIN teams_players tp2 on tp2.playerId = p2.id\
				LEFT JOIN teams t2 on tp2.teamId = t2.id\
				LEFT JOIN matches g on t2.matchId = g.id\
				WHERE g.modeId = " + modeId + " AND t2.win = 1 AND p2.id = p.id\
	"

	if useStart:
		query += "\
			AND g.createdAt >= :start\
		"
	if useEnd:
		query += "\
			AND g.createdAt < :end\
		"

	query += "\
			) AS wins\
			,\
			(\
				SELECT COUNT(*)\
				FROM players p2\
				LEFT JOIN teams_players tp2 on tp2.playerId = p2.id\
				LEFT JOIN teams t2 on tp2.teamId = t2.id\
				LEFT JOIN matches g on t2.matchId = g.id\
				WHERE g.modeId = :modeId AND t2.loss = 1 AND p2.id = p.id\
	"

	if useStart:
		query += "\
			AND g.createdAt >= :start\
		"
	if useEnd:
		query += "\
			AND g.createdAt < :end\
		"

	query += "\
			) AS losses\
		FROM players p\
		ORDER BY name;\
	"

	session = model.Model().getSession()
	connection = session.connection()
	data = connection.execute(text(query), start = start, end = end, modeId = modeId)

	points = getPlayerPoints(start, useStart, end, useEnd, modeId)
	times = getTimePlayed(start, useStart, end, useEnd, modeId)


	if request.is_xhr:
		return render_template("leaderboard/_table.html", data = data, points = points, times = times)
	else:
		return render_template("leaderboard/index.html", data = data, points = points, times = times, startDate = startFormatted, endDate = endFormatted, mode = mode)

@app.route("/leaderboard/players/<int:playerId>/", methods = ["GET"])
def leaderboard_players(playerId):

	modeId = "1"

	player = model.Model().selectById(playerModel.Player, playerId)
	players = model.Model().select(playerModel.Player)

	stats = {}

	for p in players:
		teamIds = getPlayerTeams(player.id, p.id, modeId)
		if len(teamIds) == 0:
			continue

		stat = {}
		stat["player"] = p
		stat["theirs"] = getMarksPerRound(p.id, teamIds, modeId)
		stat["yours"] = getMarksPerRound(player.id, teamIds, modeId)
		stat["games"], stat["wins"], stat["losses"], stat["winPercentage"] = getWinsAndLosses(teamIds)
		stats[p.id] = stat

	return render_template("leaderboard/players.html", player = player, stats = stats)

def getMarksPerRound(playerId, teamIds, modeId):

	query = "SELECT (\
		SELECT COUNT(*)\
		FROM marks m\
		LEFT JOIN matches g ON m.matchId = g.id\
		WHERE 1 = 1\
			AND g.modeId = " + modeId + "\
			AND g.complete = 1\
			AND m.value != 0\
			AND m.playerId = :playerId\
			AND m.teamId IN (" + teamIds + ")\
	) as marks,\
	( SELECT COUNT(playerId) \
		FROM (\
			SELECT r.playerId, r.matchId, r.teamId, r.game, r.round\
			FROM marks r\
			LEFT JOIN matches g on r.matchId = g.id\
			WHERE 1 = 1\
				AND g.modeId = " + modeId + "\
				AND g.complete = 1\
				AND r.teamId IN (" + teamIds + ")\
			GROUP BY r.playerId, r.matchId, r.teamId, r.round, r.game\
		) AS rounds\
		WHERE playerId = :playerId\
	) AS rounds\
	"

	session = model.Model().getSession()
	connection = session.connection()
	data = connection.execute(text(query), playerId = playerId).first()

	marksPerRound = 0
	if data.rounds > 0:
		marksPerRound = float(data.marks) / float(data.rounds)

	return marksPerRound

def getPlayerTeams(player1Id, player2Id, modeId):

	query = "\
		SELECT tp.teamId, count(tp.teamId) as num\
		FROM teams_players tp\
		LEFT JOIN teams t ON tp.teamId = t.id\
		LEFT JOIN matches g ON g.id = t.matchId\
		WHERE tp.playerId IN(:player1Id, :player2Id) AND g.modeId = " + modeId + " AND g.complete = 1\
		GROUP BY tp.teamId\
		HAVING num > 1\
		ORDER by tp.teamId, tp.playerId\
	"

	session = model.Model().getSession()
	connection = session.connection()
	data = connection.execute(text(query), player1Id = player1Id, player2Id = player2Id)

	ids = ""
	for row in data:
		ids = ids + str(row.teamId) + ","

	return ids[:-1]

def getPlayerPoints(start, useStart, end, useEnd, modeId):

	data = {}

	query = "\
		SELECT m.*\
		FROM marks m\
		LEFT JOIN matches g ON m.matchId = g.id\
		WHERE g.modeId = " + modeId + " AND g.complete = 1\
	"

	if useStart:
		query += "\
			AND g.createdAt >= :start\
		"
	if useEnd:
		query += "\
			AND g.createdAt < :end\
		"

	session = model.Model().getSession()
	connection = session.connection()
	marks = connection.execute(text(query), start = start, end = end)

	points = {}
	players = model.Model().select(playerModel.Player)

	for player in players:
		points[player.id] = 0

	for mark in marks:

		if not data.has_key(mark.matchId):
			data[mark.matchId] = {}

		if not data[mark.matchId].has_key(mark.teamId):
			data[mark.matchId][mark.teamId] = {}

		if not data[mark.matchId][mark.teamId].has_key(mark.game):
			data[mark.matchId][mark.teamId][mark.game] = {}

		if not data[mark.matchId][mark.teamId][mark.game].has_key(mark.value):
			data[mark.matchId][mark.teamId][mark.game][mark.value] = 0

		data[mark.matchId][mark.teamId][mark.game][mark.value] += 1

		if data[mark.matchId][mark.teamId][mark.game][mark.value] > 3:
			points[mark.playerId] += mark.value

	return points

def getTimePlayed(start, useStart, end, useEnd, modeId):

	times = {}
	players = model.Model().select(playerModel.Player)

	for player in players:
		times[player.id] = {
			"seconds": 0,
			"time": ""
		}

	query = "\
		SELECT DISTINCT p.id as playerId, g.id as matchId, UNIX_TIMESTAMP(g.createdAt) as gameTime, UNIX_TIMESTAMP(g.completedAt) as resultTime\
		FROM players p\
		LEFT JOIN teams_players tp ON p.id = tp.playerId\
		LEFT JOIN teams t ON tp.teamId = t.id\
		LEFT JOIN matches g ON t.matchId = g.id\
		WHERE g.complete = 1 AND g.modeId = " + modeId + "\
	"

	if useStart:
		query += "\
			AND g.createdAt >= :start\
		"
	if useEnd:
		query += "\
			AND g.createdAt < :end\
		"

	session = model.Model().getSession()
	connection = session.connection()
	rows = connection.execute(text(query), start = start, end = end)

	for row in rows:
		times[row.playerId]["seconds"] += row.resultTime - row.gameTime

	for playerId in times:
		times[playerId]["time"] = formatTime(times[playerId]["seconds"])

	return times

def getWinsAndLosses(teamIds):

	# query = "\
	# 	SELECT\
	# 		COUNT(*) AS games,\
	# 		SUM(win = 1) as wins,\
	# 		SUM(loss = 1) as losses,\
	# 		AVG(score) as averageScore\
	# 	FROM results\
	# 	WHERE teamId IN(" + teamIds + ")\
	# "
	query = "\
		SELECT\
			COUNT(*) AS games,\
			SUM(win = 1) as wins,\
			SUM(loss = 1) as losses\
		FROM teams\
		WHERE id IN(" + teamIds + ")\
	"

	session = model.Model().getSession()
	connection = session.connection()
	data = connection.execute(text(query)).first()

	winPercentage = 0
	if data.games > 0:
		winPercentage = data.wins / data.games

	return data.games, data.wins, data.losses, winPercentage

def formatTime(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return "%02d:%02d:%02d" % (h, m, s)


@app.route("/leaderboard/date-range/", methods = ["POST"])
def leaderboard_date_range():
	startDate = request.form["startDate"]
	endDate = request.form["endDate"]

	if len(startDate) == 0:
		startDate = None
	if len(endDate) == 0:
		endDate = None

	model.Model().update(settingModel.Setting, 1, { "startDate": startDate, "endDate": endDate })
	return ""