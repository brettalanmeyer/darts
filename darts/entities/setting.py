from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Setting(Base):

	__tablename__ = "settings"

	id = Column(Integer, primary_key = True)
	startDate = Column(DateTime)
	endDate = Column(DateTime)

	def __init__(self, startDate, endDate):
		self.startDate = startDate
		self.endDate = endDate
