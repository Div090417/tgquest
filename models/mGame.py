from sqlalchemy import (
    Table,
    Column,
    Text,
    Integer,
    String,
    Boolean,
    JSON
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship
from .meta import Base

class Quests(Base):
    __tablename__='quests'
    id = Column(String(16), primary_key=True) #unique ID with prefix Q
    name = Column(String(64)) # quest name
    short = Column(String(256)) # short description 
    start = Column(Text) # message on Q start
    finish = Column(Text) # message on Q finish
    priceGold = Column(Integer) # price for Q start
    limitHonour = Column(Integer) # Honour limit for Q start
    rewardGold = Column(Integer) # Reward for finish
    rewardHonour = Column(Integer) # Reward for finish
    steps = Column(JSON) #1:ID 2:ID ...
    
class Steps(Base):
    __tablename__='steps'
    id = Column(String(16), primary_key=True)
    task = Column(Text)
    answer = Column(String(32))
    rewardGold = Column(Integer) # Reward for finish
    rewardHonour = Column(Integer) # Reward for finish
    penaltyGold = Column(Integer)
    numberFreeTry = Column(Integer)
    #Нужно ли ставить связь с Квестом и порядковый номер?
    tips = Column(JSON) #1:ID 2:ID ...
    
class Tips(Base):
    __tablename__='tips'
    id = Column(String(16), primary_key=True)
    text = Column(Text)
    priceGold = Column(Integer) # price for Q start
    
    