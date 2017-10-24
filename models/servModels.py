#сервисные модели. Команды
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
)

from .meta import Base
import telepot
import datetime
 
class Session(Base):
    __tablename__='session'
    uid = Column(Integer, primary_key=True)
    cpos = Column(Integer) #Current Position (Route)
    lcmd = Column(String(50)) #Указатель пути. Навигационные команды можно не учитывать
    #slvl = Column(String(50)) 
    page = Column(Integer) #номер запрошенной страницы с офером
    
    def goBack(self, token, chid):
        if self.cpos > 0:
            self.cpos -= 1
        return

class Apilog(Base):
    __tablename__ = 'api_logs'
    num = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.datetime.now)
    req = Column(String(2048))
    resp = Column(String(2048))
    
class Message(Base):
    __tablename__='messages'
    cmd = Column(String(50), primary_key=True)
    text = Column(Text)
    
    def sendMessage(self, token, chid):
        bot = telepot.Bot(token)
        try:
            bot.sendMessage(chid, self.text)
            result = str(self.text)
        except:
            result = 'fail send message'
        return result

