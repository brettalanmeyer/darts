from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mode(Base):

	__tablename__ = "modes"

	id = Column(Integer, primary_key = True)
	name = Column(String)
	mode = Column(String)
	alias = Column(String)
	orderNum = Column(Integer)
	enabled = Column(Integer)

	def __init__(self, mode, alias, orderNum, enabled):
		self.name = name
		self.mode = mode
		self.alias = alias
		self.orderNum = orderNum
		self.enabled = enabled
