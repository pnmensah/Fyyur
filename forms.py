from statics import STATES, GENRES
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL

class ShowForm(Form):
    artist_id = StringField('artist_id')
    venue_id = StringField('venue_id')
    start_time = DateTimeField('start_time',validators=[DataRequired()],default= datetime.today())

class VenueForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()],choices=STATES)
    address = StringField('address', validators=[DataRequired()])
    phone = StringField('phone')
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()],choices=GENRES)
    facebook_link = StringField('facebook_link', validators=[URL()])
    website_link = StringField('website_link')
    seeking_talent = BooleanField( 'seeking_talent' )
    seeking_description = StringField('seeking_description')



class ArtistForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()],choices=STATES)
    phone = StringField('phone')
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()],choices=GENRES)
    facebook_link = StringField('facebook_link', validators=[URL()])
    website_link = StringField('website_link')
    seeking_venue = BooleanField( 'seeking_venue' )
    seeking_description = StringField('seeking_description')

