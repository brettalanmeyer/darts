from sqlalchemy import create_engine, Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()

class Game(Base):

	__tablename__ = "games"

	id = Column(Integer, primary_key = True)
	matchId = Column(Integer)
	game = Column(Integer)
	round = Column(Integer)
	start = Column(Integer)
	turn = Column(Integer)
	complete = Column(Integer)
	data = Column(String)
	winner = Column(Integer)
	winnerScore = Column(Integer)
	loser = Column(Integer)
	loserScore = Column(Integer)
	createdAt = Column(DateTime)
	completedAt = Column(DateTime)

	def __init__(self, matchId, game, start, turn, round, complete, data, createdAt):
		self.matchId = matchId
		self.game = game
		self.start = start
		self.turn = turn
		self.round = round
		self.complete = complete
		self.data = data
		self.createdAt = createdAt
