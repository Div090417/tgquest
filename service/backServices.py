from ..models import (
    Message,
    FirstLevel,
    SecondLevel,
    Session,
    Apilog,
    )

import telepot

from telepot.namedtuple import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

class BackServices:

    def __init__(self, request, token):
        api_req = request.json_body
        self.request = request
        self.token = token
        self.cses = None
        try:
            self.chid = api_req['message']['chat']['id']
            self.cmd = api_req['message']['text']
            self.msid = None
            self.q_id = None
        except:
            self.chid = api_req['callback_query']['message']['chat']['id']
            self.cmd = api_req['callback_query']['data']
            self.msid = api_req['callback_query']['message']['message_id']
            self.q_id = api_req['callback_query']['id']
        
    
    def test_myself(self):
        return self.token
    
    #создаем сессию и передаем созданный экземпляр
    
    def makesession(self):
        cses = self.request.dbsession.query(Session).get(self.chid)
        if cses:
            r = 'old session'
        #если не найден, то создаем
        if not cses:
            cses = Session()
            cses.uid = self.chid
            cses.cpos = 0 #/start
            #cses.lcmd = '/start'
            cses.page = 0
            self.request.dbsession.add(cses)
            r = 'new session'
        self.cses = cses
        return r
    
    
    def static_rout(self):
        static_commands = {
        '/start': self.startMessage, #вызываем функцию, которая отправит сообщ с приветствием
        '/help': self.sendMessage, #вызываем функцию, которая отправит инструкцию
        '/back': self.goBack,#тут надо понизить уровень и выдать список объектов своего уровня в заданной области
        '/more': self.getmore,#эта команда актуальна только на 2 уровне, действие над 2 уровнем
        'nxt': self.paginate,
        'prv': self.paginate,
        }
        try:
            func = static_commands[self.cmd]
        except:
            func = None    
        return func
        
    #отправляем сообщение при комнде старт
    
    def startMessage(self):
        try:
            #отправляем привет
            self.cses.cpos = 0
            r = self.sendMessage()
            #отправляем список 1 уровня
            self.list_first_lvl()
            self.cses.lcmd = self.cmd   
        except:
            bot = telepot.Bot(self.token)
            bot.sendMessage(self.chid, 'First Level not found')
            r = 'start failed'
        return r
    
    
    def list_first_lvl(self):
        
        clist = self.request.dbsession.query(FirstLevel).all()
        bot = telepot.Bot(self.token)
        if not clist:
            bot.sendMessage(self.chid, 'Nothing found')
            result = 'Nothing found'
            return result
        list_btns = []
        for obj in clist:
            row_btn = []
            row_btn.append(InlineKeyboardButton(text=obj.name, callback_data=obj.cmd))
            list_btns.append(row_btn)
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=list_btns)
        
        try:
            bot.sendMessage(self.chid, 'Select category:', reply_markup=reply_markup)
            result = 'markup_scs'
            self.cses.lcmd = self.cmd
        except:
            result = 'fail'
        if self.q_id:
            try:
                bot.answerCallbackQuery(self.q_id)
            except:
                self.sendDebugMessage('no callback')
        return result
    
    #отправляем некое сообщение для статик команды без специфики
    
    def sendMessage(self, custom_message=None):
        
        if custom_message:
            cobj = self.request.dbsession.query(Message).get(custom_message)
        else:
            cobj = self.request.dbsession.query(Message).get(self.cmd)
        try:
            r = cobj.sendMessage(self.token, self.chid)
            self.cses.lcmd = self.cmd
        except:
            self.sendDebugMessage('Message Not Found')
            r = 'send message failed'
        return r
    
    
    def sendData(self):
        #если команда динамическая, то она повышает уровень, если это возможно
        #исключается и кейс с нулевым уровнем
        if self.cses.cpos < 2:
            self.cses.cpos += 1
        
        lvls = {
            1: FirstLevel, #получаем список связей 2 уровня по 1 уровню
            2: SecondLevel, #получаем список связей 3 уровня по 2 уровню
            }
        
        #определяем локацию и в зав-ти от неё - адресуем, ищем объекты в БД
        try:
            cmodel = lvls[self.cses.cpos]
        except:
            r = self.sendMessage('err058')
            r = self.cses.cpos
            if self.cses.cpos > 0:
                self.cses.cpos -= 1
            return self.cses.cpos
        
        #ищем в соотв. таблице по запросу
        try:
            #пробуем получить экземпляр модели
            cobj = self.request.dbsession.query(cmodel).get(self.cmd)
        except:
            #если не получилось, то пишем, что ничего нет. Заканчиваем
            r = self.sendMessage('err062')
            if cses.cpos > 0:
                cses.cpos -= 1
            self.logging(r)
            return self.cses.cpos
        
        
        if not cobj:
            #если не найдено, то пишем, что ничего нет. Заканчиваем
            r = self.sendMessage('err067')
            if self.cses.cpos > 0:
                self.cses.cpos -= 1
            return self.logging(r)
    
        try:
            #пробуем отправить результат через метод модели
            r = cobj.sendMessage(self.token, self.chid, self.msid, self.q_id)
            self.cses.lcmd = self.cmd    
        except:
            #Если не получилось - значит что-то идет не так, заканчиваем
            r = self.sendMessage('err075')
            return self.logging(r)
        
        return r
     
    
    def goBack(self):
        #с нулевого уровня запрос не актуален
        if self.cses.cpos == 0:
            r = self.sendMessage('noback')
            return r
        #если запрос назад был отдан на 1 уровне, то показать надо полный список категорий 1 уровня.
        elif self.cses.cpos == 1:
            self.cmd = '/start'
            self.cses.cpos = 0
            r = self.list_first_lvl()
            #self.sendDebugMessage('back from 1 lvl')
        #со 2 уровня - так же, т.к. можем покзать лишь список категорий 2 уровня по выборке относительно выбранной категории 1 уровня. Однако, может появиться потребность скрыть выдачу прделожений. Технически это будет назад со 2 уровня но на второй же.   
        elif self.cses.cpos == 2:
            #надо взять выбранную категорию 2 уровня
            try:
                #пробуем получить экземпляр модели
                cobj = self.request.dbsession.query(SecondLevel).get(self.cses.lcmd)
                #теперь получив экземпляр текущей категории, узнаем её предка
                parent = cobj.f_lvl
                #а получив предка, можно его методом отправить потомков
                r = parent.sendMessage(self.token, self.chid, self.msid, self.q_id)
                #понижаем уровень
                self.cses.cpos -= 1
                
            except:
                self.sendDebugMessage('no cat')
                r = 'Fail'
            
            #self.sendDebugMessage('back from 2 lvl')
        else:
            r = 'Failed to go back'
        return r
    
    
    
    def getmore(self):
        if self.cses.cpos < 2:
            r = self.sendMessage('nomore')
            return r
        r = self.sendMessage('getmore')        
        #TODO тут нужна сложная логика с обработкой списка айдишников из сессии
        return r       
    
    def paginate(self):
    #обеспечивает последовательный вывод оферов    
        #определяем, в какой категории 2 уровня юзер находится
        try:
            cobj = self.request.dbsession.query(SecondLevel).get(self.cses.lcmd)
            
            if not self.cses.page:
                self.cses.page = 0
            
            if self.cmd == 'nxt':
                self.cses.page += 1
            elif self.cmd == 'prv':
                if self.cses.page > 0:
                    self.cses.page -= 1
                else:
                    self.sendDebugMessage('Cant step backward')
            
            cobj.sendMessage(self.token, self.chid, self.msid, self.q_id, self.cses.page)
        except:
            self.sendDebugMessage('Paginate Err')
    #логируем. Функция самостоятельна. 
    
    def logging(self, response=None):
        nlog = Apilog()
        nlog.req = str(self.request.json_body)
        if response:
            nlog.resp = response
        try:
            self.request.dbsession.add(nlog)
        except:
            pass
        return response

    def sendDebugMessage(self, sysmsg):
        bot = telepot.Bot(self.token)
        bot.sendMessage(self.chid, sysmsg)

