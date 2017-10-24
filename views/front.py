from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPForbidden


from ..service.backServices import BackServices


#TODO убрать в конфиг
token = '291714552:AAEEbicl_io29d9Ui7M_aT8Q-j-V0oEi21k'

@view_config(route_name='welcome', renderer='string')
def welcome(request):
    return 'Welocme to GoOut Bot page. Contact us @Divergent15'

@view_config(route_name='basic', renderer='string')
def basic(request):
    if request.matchdict['bot_token'] != token:
        return HTTPForbidden()
             
    #создаем экземпляр класса БС, чтобы получить возмжность обратиться к self
    back_service = BackServices(request, token)
    
    '''test = back_service.test_myself()
    if test:
        return test'''
        
    #открываем сессию    
    s = back_service.makesession()
    
    '''
    В систему могут прийти следующие типы команд:
    - статическая из сообщения
    - динамическая из сообщения
    - статическая из колбэка
    - динамичекая из колбэка
    
    система построена таким образом, что команды из колбэков всегда отличаются от команд из сообщений
    
    Таким образом, первичным фильтром может быть проверка на тип входящего сообщения.
    Тем более, что для работы с разными типами - используются и разные методы
    
    Большинство команд являются контекстно зависимыми, т.е. нам важно знать предыдушие команды и состояние системы.
    Но есть ряд команд не зависящих от контекста. И в нынешней реализации они выбивают контекст, что приводит к ошибкам.
    Для исправления - нужно не менять состояние системы при выполнении независимых команд
    '''
    
    #проверяем команду на соотв. статическим. Через словарь - для исключения лишенго запроса к БД 
    func = back_service.static_rout()
    if func:
        r = func()
        return back_service.logging(r)
        
    
    ###########################################
    ###                                     ###
    ### Блок обработки динамических команд  ###
    ###                                     ###
    ###########################################
    else:
        r = back_service.sendData()
        
    return back_service.logging(r)
    #return FrontServices.logging(request, r)


