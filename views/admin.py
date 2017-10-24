from pyramid.response import Response
from pyramid.view import view_config

from webob.multidict import MultiDict as md

from ..models import (
    FirstLevel, SecondLevel, Offer,
    Manager, User,
    Session, Apilog, Message    
    )

from ..service.panel_obj import PanelObjService
from ..service.panel_forms import (
    standartFields,
    SecondLevelFields,
    OfferFields,
    MessageFields,
    LoginForm
    )

from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound,
    HTTPForbidden,
)

####################
## SECOND EDITION ##
####################

###########
## LISTS ##
###########
@view_config(route_name='panel_list', renderer='../templates/panel/p_list.jinja2', permission='create')
def panel_list(request):
    page = int(request.params.get('page', 1))
    otype = request.matchdict['type']
    types = {
        'mes': Message,
        'frst': FirstLevel,
        'scnd': SecondLevel,
        'offrs': Offer,
    }
    message = {
        'mes': 'List of Messages',
        'frst': 'List of First Level Categories',
        'scnd': 'List of Second Level Categories',
        'offrs': 'List of Offers',
    }
    model = types[otype]
    paginator = PanelObjService.get_paginator(request, model, page)
    return dict(view_name=message[otype], paginator=paginator, otype=otype)
    
#############
## OBJECTS ##
#############
@view_config(route_name='panel_object', renderer='../templates/panel/p_edit.jinja2', permission='create')    
def panel_object(request):
    # задаём базовые переменные
    slug = request.matchdict['slug']
    otype = request.matchdict['type']
    types = {
        'mes': Message,
        'frst': FirstLevel,
        'scnd': SecondLevel,
        'offrs': Offer,
    }
    new_message = {
        'mes': 'Create new Message',
        'frst': 'Create new First Level Category',
        'scnd': 'Create new Second Level Category',
        'offrs': 'Create new Offer',
    }
    edit_message = {
        'mes': 'Edit Message',
        'frst': 'Edit First Level Category',
        'scnd': 'Edit Second Level Category',
        'offrs': 'Edit Offer',
    }
    model = types[otype]
    
    if slug == 'new':
        message = new_message[otype]
        if otype == 'mes':
            form = MessageFields(request.POST)            
        elif otype == 'frst':
            form = standartFields(request.POST)
        elif otype == 'scnd':
            form = SecondLevelFields(request.POST)
            #получаем список категорий 1 уровня
            #message = request.dbsession.query(FirstLevel).all()
            try:
                form.parent.choices = [(c.cmd, c.name) for c in request.dbsession.query(FirstLevel).all()]
            except:
                form.parent.choices = [('none', 'None')]
            
        elif otype == 'offrs':
            form = OfferFields(request.POST)
            #получаем список категорий 2 уровня
            try:
                form.parent.choices = [(c.cmd, c.name) for c in request.dbsession.query(SecondLevel).all()]
            except:
                form.parent.choices = [('none', 'None')]
        
        #попытка записи в БД
        if request.method == 'POST' and form.validate():
                #проверка на уникальность
                if request.dbsession.query(model).filter_by(cmd=request.params['cmd']).one_or_none():                    
                    form.cmd.errors.append('Cmd is not unique')
                    return dict(view_name=message, form=form, slug=slug, otype=otype)                   
                inst = model()
                
                #начинаем писать в БД
                try:
                    #общие параметры для всех
                    inst.cmd = request.params['cmd']
                    inst.text = request.params['text']                    
                except:
                    form.cmd.errors.append('You cant add this command')
                    return dict(view_name=message, form=form, slug=slug, otype=otype)
                
                
                if otype == 'frst':
                    #Если пишем первый уровень - добавляем параметр Имя
                    inst.name = request.params['name']
                    
                elif otype == 'scnd':
                    #Если пишем 2 уровень - добавляем ещё параметры
                    inst.name = request.params['name']
                    if request.params['parent']:    
                        try:
                            inst.f_lvl = request.dbsession.query(FirstLevel).get(request.params['parent'])
                        except:
                            form.parent.errors.append('Append Error')
                            
                            return dict(view_name=message, form=form, slug=slug, otype=otype)
                                
                elif otype == 'offrs':
                    inst.name = request.params['name']
                    inst.link = request.params['link']
                    inst.image = request.params['image']
                    try:
                        if request.params['active']:
                            inst.active = True
                    except:
                        inst.active = False
                    try:
                        inst.date_expired = request.params['date_expired']
                    except:
                        form.date_expired.errors.append('incorrect date format:_'+request.params['date_expired'])
                    try:
                        if request.params['parent']:
                            params = md.dict_of_lists(request.POST)
                            inst.s_lvl.clear()
                            for p in params['parent']:
                                inst.s_lvl.append(request.dbsession.query(SecondLevel).get(p))
                    except:
                         
                        form.parent.errors.append('Append Error')
                        return dict(view_name=message, form=form, slug=slug, otype=otype)

                request.dbsession.add(inst)
                
                return HTTPFound(location=request.route_url('panel_list', type=otype))
        return dict(view_name=message, form=form, slug=slug, otype=otype)
    else:
        ##############################
        ### редактирование Объекта ###
        ##############################
        
        message = edit_message[otype]
        #TODO Здесь может быть не соотв ссылок и первичных ключей
        entry = request.dbsession.query(model).get(slug)
        if not entry:
            raise HTTPNotFound()
        #создаем формы для каждого объекта
        if otype == 'mes':
            form = MessageFields(request.POST, entry)            
        
        elif otype == 'frst':
            form = standartFields(request.POST, entry)            
        
        elif otype == 'scnd':
            form = SecondLevelFields(request.POST, entry)
            
            try:
                #создаем список возможных связей c первым уровнем:
                form.parent.choices = [(c.cmd, c.name) for c in request.dbsession.query(FirstLevel).all()]
                #отмечаем выбранные
                form.parent.data = entry.f_lvl.cmd
            except:
                form.parent.choices = [('none', 'None')]
            
           
        
        elif otype == 'offrs':
            form = OfferFields(request.POST, entry)
            
            
            try:
                #получаем список категорий 2 уровня
                form.parent.choices = [(c.cmd, c.name) for c in request.dbsession.query(SecondLevel).all()]
                #отмечаем выбранные
                form.parent.data = [e.cmd for e in entry.s_lvl]
            except:
                form.parent.choices = [('none', 'None')]
        
        ### запись в БД ###
        if request.method == 'POST' and form.validate():
            try:
                entry.cmd = request.params['cmd']
                entry.text = request.params['text']
            except:
                    form.cmd.errors.append('You cant add this command')
                    return dict(view_name=message, form=form, slug=slug, otype=otype)
            
            if otype == 'frst':
                    #Если пишем первый уровень - добавляем параметр Имя
                    entry.name = request.params['name']
            
            elif otype == 'scnd':
                    #Если пишем 2 уровень - добавляем ещё параметры
                    entry.name = request.params['name']
                    if request.params['parent']:    
                        try:
                            
                            entry.f_lvl = request.dbsession.query(FirstLevel).get(request.params['parent'])
                        except:
                            form.parent.errors.append('Append Error')
                            
                            return dict(view_name=message, form=form, slug=slug, otype=otype)
        
            elif otype == 'offrs':
                    entry.name = request.params['name']
                    entry.link = request.params['link']
                    entry.image = request.params['image']
                    try:
                        if request.params['active']:
                            entry.active = True
                    except:
                        entry.active = False
                    try:
                        entry.date_expired = request.params['date_expired']
                    except:
                        form.date_expired.errors.append('incorrect date format:_'+request.params['date_expired'])
                    try:
                        if request.params['parent']:
                            params = md.dict_of_lists(request.POST)
                            entry.s_lvl.clear()
                            for p in params['parent']:
                                entry.s_lvl.append(request.dbsession.query(SecondLevel).get(p))
                    except: 
                        form.parent.errors.append('Append Error')
                        return dict(view_name=message, form=form, slug=slug, otype=otype)
            
            return HTTPFound(location=request.route_url('panel_list', type=otype))
            
    return dict(view_name=message, form=form, slug=slug, otype=otype)

    
