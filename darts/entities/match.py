from sqlalchemy import create_engine, Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()

class Match(Base):

	__tablename__ = "matches"

	id = Column(Integer, primary_key = True)
	modeId = Column(Integer)
	players = Column(Integer)
	games = Column(Integer)
	game = Column(Integer)
	round = Column(Integer)
	ready = Column(Integer)
	turn = Column(Integer)
	complete = Column(Integer)
	data = Column(String)
	createdAt = Column(DateTime)
	completedAt = Column(DateTime)

	def __init__(self, modeId, players, games, game, round, ready, complete, data, createdAt):
		self.modeId = modeId
		self.players = players
		self.games = games
		self.game = game
		self.round = round
		self.ready = ready
		self.complete = complete
		self.data = data
		self.createdAt = createdAt
