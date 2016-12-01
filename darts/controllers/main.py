from darts import app
from flask import render_template, request
from darts import model
from sqlalchemy import text
from darts.entities import game as gameModel
from darts.controllers.modes import cricket

@app.route("/")
def main_index():
	return render_template("main/index.html")

@app.route("/migrate-data/")
def main_migrate_data():

	session = model.Model().getSession()
	connection = session.connection()

	test = "SELECT COUNT(*) as num FROM games"
	count = connection.execute(text(test)).first()

	if count.num > 0:
		return "data already migrated!"

	datumQuery = "\
		SELECT marks.matchId, marks.game, GROUP_CONCAT(DISTINCT marks.value ORDER BY marks.value DESC) AS numbers\
		FROM marks\
		JOIN matches ON marks.matchId = matches.id\
		WHERE matches.modeId = 21 AND marks.value != 25 AND marks.value != 0\
		GROUP BY marks.matchId, marks.game;\
	"
	datum = connection.execute(text(datumQuery))
	values = {}

	for row in datum:
		if not values.has_key(row.matchId):
			values[row.matchId] = {}

		if not values[row.matchId].has_key(row.game):
			values[row.matchId][row.game] = row.numbers


	query = "\
		SELECT m.id, m.modeId, m.game, m.games, m.createdAt, m.completedAt, GROUP_CONCAT(tp.playerId) as playerIds\
		FROM matches m\
		INNER JOIN teams t ON m.id = t.matchId\
		INNER JOIN teams_players tp ON t.id = tp.teamId\
		WHERE m.modeId IN (1,21)\
			AND m.games IS NOT NULL\
		GROUP BY m.id\
	"
	matches = connection.execute(text(query))

	for match in matches:

		for i in range(1, int(match.games) + 1):

			winnerQuery = "\
				SELECT score, teamId\
				FROM results\
				WHERE matchId = :matchId AND game = :game AND win = 1\
			"
			winner = connection.execute(text(winnerQuery), matchId = match.id, game = i).first()

			loserQuery = "\
				SELECT score, teamId\
				FROM results\
				WHERE matchId = :matchId AND game = :game AND loss = 1\
			"
			loser = connection.execute(text(loserQuery), matchId = match.id, game = i).first()

			insert = "\
				INSERT INTO `games` (`matchId`, `game`, `data`, `start`, `turn`, `round`, `complete`, `winner`, `winnerScore`, `loser`, `loserScore`, `createdAt`, `completedAt`)\
				VALUES (:matchId, :game, :data, :start, :turn, 1, :complete, :winner, :winnerScore, :loser, :loserScore, :createdAt, :completedAt);\
			"

			player = getPlayer(match.playerIds, i)

			data = "20,19,18,17,16,15"

			if match.modeId == 21:
				data = getData(values, int(match.id), i)

			connection.execute(
				text(insert),
				matchId = match.id,
				game = i,
				data = data,
				start = player,
				turn = player,
				complete = winner != None,
				winner = winner.teamId if winner != None else None,
				winnerScore = winner.score if winner != None else None,
				loser = loser.teamId if loser != None else None,
				loserScore = loser.score if loser != None else None,
				createdAt = match.createdAt,
				completedAt = match.completedAt
			)

	session.commit()
	session.close()

	return "done"


def getPlayer(playerIds, game):
	ids = playerIds.split(",")

	if len(ids) == 2:
		if game % 2 == 1:
			return ids[0]

		return ids[1]

	if len(ids) == 4:
		if game == 1:
			return ids[0]

		if game == 2:
			return ids[2]

		if game == 3:
			return ids[1]

		if game == 4:
			return ids[3]

		return ids[0]

	return None

def getData(datum, matchId, game):
	if datum.has_key(matchId) and datum[matchId].has_key(game):
		return  datum[matchId][game]

	return cricket.cricket_points("random-crickets")
