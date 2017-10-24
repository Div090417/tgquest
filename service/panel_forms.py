from wtforms import (
    Form,
    StringField, 
    TextAreaField, 
    IntegerField, 
    BooleanField, 
    SelectField, 
    SelectMultipleField, 
    validators, 
    PasswordField,
    FormField,
    DateField,
)

strip_filter = lambda x: x.strip() if x else None

### Content Models ###

class standartFields(Form):
    cmd = StringField('The calling command',
        [validators.Length(min=1, max=32, message='must be from 1 to 50')], filters=[strip_filter])
    name = StringField('Name',
        [validators.Length(min=1, max=32, message='must be from 1 to 50')], filters=[strip_filter])
    text = StringField('Description',
        [validators.Length(min=0, max=512, message='must be from 1 to 50')], filters=[strip_filter])

class SecondLevelFields(standartFields):
    parent = SelectField('Related First Level')

class OfferFields(standartFields):
    link = StringField('Link to external Offer (512 symbols limit)',
        [validators.Length(min=0, max=512, message='must be from 1 to 50')], filters=[strip_filter])
    image = StringField('Link to external Image (512 symbols limit)',
        [validators.Length(min=0, max=512, message='must be from 1 to 50')], filters=[strip_filter])
    parent = SelectMultipleField('Related Second Level')
    date_expired = DateField('Date Expired: Y-m-d')
    active = BooleanField('Is Active?')
    
### Services Models ###

class MessageFields(Form):
    cmd = StringField('The calling command',
        [validators.Length(min=1, max=32, message='must be from 1 to 50')], filters=[strip_filter])
    text = StringField('Text for User',
        [validators.Length(min=1, max=512, message='must be from 1 to 50')], filters=[strip_filter])
    
    
class LoginForm(Form):
    username = StringField('Name',
        [validators.Length(min=1, max=30, message='must be from 1 to 30')])
    password = PasswordField('Password',
        [validators.Length(min=1, max=30, message='must be from 1 to 30')])
