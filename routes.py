# Gout SE Bot - Routes
def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    config.add_route('welcome', '/')
    
    ############
    ### AUTH ###
    ############
    config.add_route('panel_index', '/editor/',
        factory='goutse.security.AdminPanelFactory')
    #Корневая страница админки, навигация по разделам, закрыто для гостя
    config.add_route('panel_auth_form', '/editor/auth/')
    #для гостя - форма входа, для юзера - редирект на корневую
    config.add_route('panel_auth_out', '/editor/auth/out')
    #логинит или разлогинивает пользователя. не имеет своего отображения
    
    ##############
    ### EDITOR ###
    ##############
    config.add_route('panel_list', '/editor/{type}/',
        factory='goutse.security.AdminPanelFactory')
    #Список объектов
    config.add_route('panel_object', '/editor/{type}/{slug}',
        factory='goutse.security.AdminPanelFactory') 
    #Создание и редактирование объекта
    
    ##############
    ### FRONT ###
    ##############
    config.add_route('basic', '/{bot_token}')
    
    
