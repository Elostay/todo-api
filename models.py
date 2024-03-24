from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class Todos(Base):
	__tablename__ = 'todos'

	_id = Column(Integer, primary_key=True, index=True)
	task = Column(String, index=True)
	rate = Column(Integer, index=True)
	done = Column(Boolean, default=False)