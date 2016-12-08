from darts import app
from flask import Response, render_template, redirect, request
from darts.entities import match as matchModel
from darts.entities import player as playerModel
from darts.entities import team as teamModel
from darts.entities import team_player as teamPlayerModel
from darts.entities import mark as markModel
from darts.entities import mode as modeModel
from darts.entities import game as gameModel
from darts import model
from datetime import datetime
from sqlalchemy import desc
import operator, json, math

@app.route("/matches/", methods = ["GET"], defaults = { "page": 1 })
@app.route("/matches/<int:page>/", methods = ["GET"])
def matches_index(page):

	paging = {
		"total": 0,
		"page": page,
		"limit": 40,
		"pages": 0
	}

	data = []

	matches = model.Model().select(matchModel.Match).filter(matchModel.Match.ready == True, ((matchModel.Match.modeId == 1) | (matchModel.Match.modeId == 21))).order_by(desc("createdAt"))

	paging["total"] = matches.count()
	matches = matches.limit(paging["limit"]).offset((page - 1) * paging["limit"]).all()

	players = model.Model().select(playerModel.Player)
	playerDict = {}
	for player in players:
		playerDict[player.id] = player

	results = model.Model().select(gameModel.Game)
	resultDict = {}
	for result in results:
		if not resultDict.has_key(result.matchId):
			resultDict[result.matchId] = {}
		if not resultDict[result.matchId].has_key(result.winner):
			resultDict[result.matchId][result.winner] = []
		if not resultDict[result.matchId].has_key(result.loser):
			resultDict[result.matchId][result.loser] = []

		resultDict[result.matchId][result.winner].append({
			"score": result.winnerScore,
			"win": True,
			"loss": False
		})
		resultDict[result.matchId][result.loser].append({
			"score": result.loserScore,
			"win": False,
			"loss": True
		})

	for match in matches:

		if match.modeId == 1:
			mode = "Cricket"
		else:
			mode = "Random Crickets"

		matchData = {
			"id": match.id,
			"mode": mode,
			"date": "{:%b %d, %Y} ".format(match.createdAt),
			"time": "{:%I:%M %p}".format(match.createdAt).lower(),
			"duration": None,
			"teams": []
		}

		if match.completedAt != None:
			duration = match.completedAt - match.createdAt
			matchData["duration"] = duration

		teams = model.Model().select(teamModel.Team).filter_by(matchId = match.id)

		for team in teams:

			teamData = {
				"id": team.id,
				"mark": 0,
				"players": [],
				"points": 0,
				"win": team.win,
				"loss": team.loss
			}

			players = model.Model().select(teamPlayerModel.TeamPlayer).filter_by(teamId = team.id)

			for player in players:
				teamData["players"].append(playerDict[player.playerId].name)

			matchData["teams"].append(teamData)

		data.append(matchData)

		matchData["teams"].sort(key = operator.itemgetter("mark"), reverse = True)

	paging["pages"] = int(math.ceil(paging["total"] / float(paging["limit"])))

	return render_template("matches/index.html", matches = data, results = resultDict, paging = paging)

@app.route("/matches/new/", methods = ["GET"])
def matches_new():
	modes = model.Model().select(modeModel.Mode).filter_by(enabled = True).order_by("orderNum")
	return render_template("matches/new.html", modes = modes)

@app.route("/matches/", methods = ["POST"])
def matches_create():
	newMatch = matchModel.Match(request.form["modes"], None, None, 1, 1, False, 0, datetime.now())
	model.Model().create(newMatch)

	mode = model.Model().selectById(modeModel.Mode, newMatch.modeId)
	return redirect("/matches/%d/modes/%s/" % (newMatch.id, mode.alias))
