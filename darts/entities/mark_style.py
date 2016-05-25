from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MarkStyle(Base):

	__tablename__ = "mark_styles"

	id = Column(Integer, primary_key = True)
	name = Column(String)
	email = Column(String)
	token = Column(String)
	one = Column(String)
	two = Column(String)
	three = Column(String)
	confirmed = Column(Integer)
	approved = Column(Integer)
	createdAt = Column(DateTime)

	def __init__(self, name, email, token, one, two, three, confirmed, approved, createdAt):
		self.name = name
		self.email = email
		self.token = token
		self.one = one
		self.two = two
		self.three = three
		self.confirmed = confirmed
		self.approved = approved
		self.createdAt = createdAt
