# ==================================================================================================================== #
# Imports
# ==================================================================================================================== #

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from datetime import datetime


# ==================================================================================================================== #
# App Config.
# ==================================================================================================================== #

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ==================================================================================================================== #
# Models.
# ==================================================================================================================== #

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website_link = db.Column(db.String)
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue')
    # city_id = db.Column(db.Integer, db.ForeignKey('City.id'), nullable=False)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    website_link = db.Column(db.String)
    shows = db.relationship('Show', backref='artist')


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    start_time = db.Column(db.DateTime())
