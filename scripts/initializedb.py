import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import (
    FirstLevel, SecondLevel, Offer,
    Manager, User,
    Session, Apilog, Message
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        '''
        admin = Manager(login='admin', name='First Admin', role='admin')
        admin.set_password('aadminn')
        dbsession.add(admin)
        
        msg = Message(cmd='/start', text='Welcome to Go Out Alfa test')
        dbsession.add(msg)
        
        msg = Message(cmd='/help', text='Some help')
        dbsession.add(msg)
        
        msg = Message(cmd='/back', text='Back is not available')
        dbsession.add(msg)
        
        msg = Message(cmd='noback', text='You cant go back from here')
        dbsession.add(msg)
        
        msg = Message(cmd='back', text='BACK command is not available')
        dbsession.add(msg)
        
        msg = Message(cmd='nomore', text='You cant get more')
        dbsession.add(msg)
        
        msg = Message(cmd='more', text='MORE command is not available')
        dbsession.add(msg)
        
        msg = Message(cmd='err062', text='err062')
        dbsession.add(msg)
        
        msg = Message(cmd='err067', text='err067')
        dbsession.add(msg)
        
        msg = Message(cmd='err075', text='err075')
        dbsession.add(msg)
        
        msg = Message(cmd='err058', text='err058')
        dbsession.add(msg)
        
        
        
        flvl = FirstLevel(cmd='cafe', name='Drink Cofee', text='cafe')
        dbsession.add(flvl)
        
        flvl = FirstLevel(cmd='pub', name='Pick some Bear', text='bear')
        dbsession.add(flvl)
        
        flvl = FirstLevel(cmd='restaraunt', name='Eat taste food', text='some food')
        dbsession.add(flvl)
        '''
        
        
