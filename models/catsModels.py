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

from sqlalchemy.orm import relationship
from .meta import Base

import telepot

from telepot.namedtuple import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

offer_to_slvl_tbl = Table('offer_to_scndlvl',  Base.metadata,
    Column('offer', String(50), ForeignKey('offers.cmd')),
    Column('s_lvl', String(50), ForeignKey('cat_second.cmd')),
)
   
class FirstLevel(Base):
    __tablename__='cat_first'
    cmd = Column(String(50), primary_key=True)
    name = Column(String(50), unique=True)
    text = Column(Text)
    
    s_lvl = relationship("SecondLevel", back_populates='f_lvl')
        
    def sendMessage(self, token, chid, msg_id=None, q_id=None):
        bot = telepot.Bot(token)
        #получить список дочерних объектов
        lst = self.s_lvl
        msg = self.text
        #######
        emc = None
        acq = None
        #######
        #сформировать инлайн клавиатуру
        if lst:
            list_btns = []
            for obj in lst:
                row_btn = []
                row_btn.append(InlineKeyboardButton(text=obj.name, callback_data=obj.cmd))
                list_btns.append(row_btn)
                #bot.sendMessage(chid, obj.name)
            row_btn = []
            row_btn.append(InlineKeyboardButton(text='<-- Go Back --', callback_data='/back'))
            list_btns.append(row_btn)
            reply_markup = InlineKeyboardMarkup(inline_keyboard=list_btns)
            
        else:
            msg = 'Nothing found in this category'
        #отправить сообщение
        if msg_id:
            edit_id = (chid, msg_id)
            try:
                #bot.editMessageCaption((chid, msg_id), 'Caption', reply_markup)
                bot.editMessageText(edit_id, msg)
                bot.editMessageReplyMarkup(edit_id, reply_markup)
                emc = 'scs'
            except:
                emc = 'Fail'
            try:
                bot.answerCallbackQuery(q_id)
                #bot.answerCallbackQuery(q_id, 'Inline answer')
                acq = 'scs'
            except:
                acq = 'Fail'
        else:
            bot.sendMessage(chid, msg, reply_markup)
            
        result = dict(emc=emc, acq=acq, edit_id=edit_id, q_id=q_id)
        return str(result)

class SecondLevel(Base):
    __tablename__='cat_second'
    cmd = Column(String(50), primary_key=True)
    name = Column(String(50), unique=True)
    text = Column(Text)
    
    #Child to Parent (Many to One)
    f_lvl_id = Column(String(50), ForeignKey('cat_first.cmd'))
    f_lvl = relationship("FirstLevel", back_populates='s_lvl')
    
    r_offers = relationship("Offer", secondary=offer_to_slvl_tbl, back_populates='s_lvl')
    
    def sendMessage(self, token, chid, msg_id=None, q_id=None, page=0):
        bot = telepot.Bot(token)
        r_offers = self.r_offers
        offer_list =[]
        for o in r_offers:
            offer_list.append(o)
        
        mxlim = len(offer_list) - 1
        if page > mxlim:
            pg = mxlim
        else:
            pg = page
        offer = offer_list.pop(pg)
        
        message = offer.name + '\n' + offer.text + '\n--------------'
        #сформировать инлайн клавиатуру
        if not offer.link:
            offer.link = 'http://ya.ru'
        list_btns = []
        row_btn = []
        row_btn.append(InlineKeyboardButton(text='Get your offer', url=offer.link))
        list_btns.append(row_btn)
        row_btn = []
        if page > 0:
            row_btn.append(InlineKeyboardButton(text='<- Previous', callback_data='prv'))
        if page < mxlim:
            row_btn.append(InlineKeyboardButton(text='Next ->', callback_data='nxt'))
        list_btns.append(row_btn)
        row_btn = []
        row_btn.append(InlineKeyboardButton(text='<-- Go Back --', callback_data='/back'))
        list_btns.append(row_btn)
        
        '''
        #сформировать блок офферов
        bot.sendMessage(chid, 'Here are your offers:')
        for offer in r_offers:
            message = offer.name + '\n' + offer.text + '\n' + offer.link + '\n'
            try:
                #отправить каждый офер в новом сообщении 
                bot.sendMessage(chid, message)
                result += str(offer.name) + '||'
            except:
                result = 'Second Level fail'
        
        #сформировать инлайн клавиатуру c кнопкой Назад
        list_btns = []
        row_btn = []
        row_btn.append(InlineKeyboardButton(text='<-- Go Back --', callback_data='/back'))
        list_btns.append(row_btn)
        
        '''   
        reply_markup = InlineKeyboardMarkup(inline_keyboard=list_btns)
        edit_id = (chid, msg_id)
        bot.editMessageText(edit_id, message)
        bot.editMessageReplyMarkup(edit_id, reply_markup)
        bot.answerCallbackQuery(q_id)
        result = offer.name
        return result
        
    def getMore(self, token, chid):
        return

class Offer(Base):
    __tablename__='offers' 
    cmd = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False)
    text = Column(Text)
    link = Column(String(512))
    image = Column(String(512))
    date_expired = Column(DateTime)
    active = Column(Boolean(name='active_flag'), default=False)
    
    #many to many (один офер может быть связан со многими категориями)
    s_lvl = relationship("SecondLevel", secondary=offer_to_slvl_tbl, back_populates='r_offers')
    
    
    
