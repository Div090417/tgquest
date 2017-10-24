from pyramid.view import (
    view_config,
    forbidden_view_config,
)

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
)

from pyramid.security import (
    remember,
    forget,
    )

from ..service.panel_forms import LoginForm
from ..models import Manager

#def check_auth(request):
    

@view_config(route_name='panel_index', renderer='../templates/panel/p_main.jinja2', permission='create')
def panel_index(request):
    
    return dict(view_name='Editor Main Page')
    
@view_config(route_name='panel_auth_form', renderer='../templates/panel/p_auth.jinja2')
def panel_exception(request):
    form = LoginForm(request.POST)
    if request.method == 'POST' and form.validate():
        user = request.dbsession.query(Manager).get(request.params['username'])
        if user == None:
            form.username.errors.append('Name is not found')
        if user and user.check_password(request.params['password']):
                headers = remember(request, user.name)
                return HTTPFound(location=request.route_url('panel_index'), headers=headers)
        form.password.errors.append('Wrong password')
        return dict(info='Invalid Credentials', form=form)
    return dict(info='Welcome to Editor', form=form)

@view_config(route_name='panel_auth_out')
def panel_auth(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('panel_auth_form'), headers=headers)
    
@forbidden_view_config()
def forbidden_view(request): 
    return HTTPFound(location=request.route_url('panel_auth_form'))    
