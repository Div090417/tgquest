import sqlalchemy as sa
from paginate_sqlalchemy import SqlalchemyOrmPage



class PanelObjService(object):

    @classmethod
    def get_paginator(cls, request, model, page=1):
        query = request.dbsession.query(model)
        query_params = request.GET.mixed()
        
        def url_maker(link_page):
            query_params['page'] = link_page
            return request.current_route_url(_query=query_params)
                
        return SqlalchemyOrmPage(query, page, items_per_page=30, url_maker=url_maker)
    
    @staticmethod
    def ArticleActions(request, model, entry, rcat, rtag):
        params = md.dict_of_lists(request.POST)
        if not entry:
            inst = model()
        else:
            inst = entry
        inst.slug = request.params['slug']
        inst.name = request.params['name']
        inst.sort = request.params['sort']
        inst.descr = request.params['descr']
        inst.preview = request.params['preview']
        inst.body = request.params['body']
        inst.category = request.dbsession.query(rcat).get(request.params['pcategory'])
        try:
            if request.params['active']:
                inst.active = True
        except:
            inst.active = False
        
        try:
            if request.params['rtags']:
                inst.related_tag.clear()
                for tag in params['rtags']:
                    inst.related_tag.append(request.dbsession.query(rtag).get(tag))
        except:
            pass
        
        try:
            if request.params['sarts']:
                inst.similar_articles.clear()
                for art in params['sarts']:
                    inst.similar_articles.append(request.dbsession.query(model).get(art))
        except:
            pass
        
        return inst
