from sqlalchemy import (
    Table,
    Column,
    Text,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
)

from .meta import Base
import datetime
import bcrypt

class Manager(Base):
    __tablename__ = 'managers'
    login = Column(String(30), primary_key=True)
    password_hash = Column(Text)
    name = Column(String(50), nullable=False)
    role = Column(String(30), nullable=False, default='admin')
    	
    def set_password(self, pw):
        pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = pwhash.decode('utf8')
    
    def check_password(self, pw):
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False
        
class User(Base):
    __tablename__ = 'app_users'
    uid = Column(Integer, primary_key=True)
    tid = Column(String(50))
    name = Column(String(50))
    regdate = Column(DateTime, default=datetime.datetime.now)
    lastactive = Column(DateTime)
