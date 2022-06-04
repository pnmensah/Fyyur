#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from ssl import CHANNEL_BINDING_TYPES
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# app = Flask(__name__)
# moment = Moment(app)
# app.config.from_object('config')
# db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    data = []
    cities = Venue.query.distinct(Venue.city, Venue.state).all()
    for city in cities:
        venues = Venue.query.filter_by(city=city.city, state=city.state).all()
        data.append({
            "city": city.city,
            "state": city.state,
            "venues": venues
        })
    return render_template('pages/venues.html', areas=data)

    # # cities = db.session.Venue.query.distinct(Venue.city, Venue.state).all()
    # cities = Venue.query.with_entities(Venue.city, Venue.state).group_by(
    #     Venue.id, Venue.city, Venue.state).distinct().all()
    # print(cities)

    # for city in cities:
    #     print(cities)

    # for city in cities:
    #     venues_in_city = db.session.query(Venue.id, Venue.name).filter(
    #         Venue.city == city[0]).filter(Venue.state == city[1])
    #     data.append({
    #         "city": city[0],
    #         "state": city[1],
    #         "venues": venues_in_city
    #     })

    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    #   data = [{
    #     "city": city,
    #     "state": state,
    #     "venues": venues
    #   }]
    #       return render_template('pages/venues.html', areas=data)

    # return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

    search_value = request.form.get("search_term", "" "")
    venues_list = db.session.query(Venue).all()
    data = []
    for venue in venues_list:
        if (venue.name).lower() == search_value.lower():
            data.append(venue)
    data_count = len(data)
    print(data)
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', data=data, data_count=data_count, search_value=search_value)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venues = Venue.query.get(venue_id)
    shows = db.session.query(Show).filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    for show in shows:
        artist = db.session.query(Artist).filter_by(id=show.artist_id).first()
        show_data = {
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time
        }
        if show.start_time < datetime.now():
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)
    data = {
        "id": venue_id,
        "name": venues.name,
        "genres": venues.genres,
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website_link": venues.website_link,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.seeking_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_venue.html', venue=data)
    # # venue = Venue.query.get(venue_id)

    # # shows the venue page with the given venue_id

    # return render_template('pages/show_venue.html', venue=venue.serialized_data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():

    # Creating a venue from form

    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)
    # if form.validate():
    try:
        venue = Venue(
            name=form.name.data,
            genres=form.genres.data,
            city=form.city.data,
            phone=form.phone.data,
            state=form.state.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            address=form.address.data,
            facebook_link=form.facebook_link.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was listed successfully!')
    except:
        db.session.rollback()
        flash('Venue ' + request.form['name'] +
              ' was listed successfully!')
    finally:
        db.session.close()

    # else:
    #     print("", form.errors)
    #     flash('An error occurred. Venue ' +
    #           form.data.name + 'was not listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/venues.html')
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=data)
    # artists_list = db.session.query(Artist).all()
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    # return render_template('pages/artists.html', artists=artists_list)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    search_result = db.session.query(Artist).filter(
        Artist.name.ilike('%' + search_term + '%')).all()
    response = {
        "count": len(search_result),
        "data": search_result
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)
    # search_value = request.form.get("search_term", "" "")
    # artists_list = db.session.query(Artist).all()
    # data = []
    # for artist in artists_list:
    #     if (artist.name).lower() == search_value.lower():
    #         data.append(artist)
    # data_count = len(data)
    # print(data)

    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    # return render_template('pages/search_artists.html', data=data, data_count=data_count, search_value=search_value)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # artist = Artist.query.get(artist_id)

    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = db.session.query(Artist).get(artist_id)
    past_shows = db.session.query(Show).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows = db.session.query(Show).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)

    # data1={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "past_shows": [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 5,
    #   "name": "Matt Quevedo",
    #   "genres": ["Jazz"],
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "300-400-5000",
    #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "past_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    #   "genres": ["Jazz", "Classical"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "432-325-5432",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             artist_id, [data1, data2, data3]))[0]
    # return render_template('pages/show_artist.html', artist=artist.serialized_data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist.genres = artist.genres.split(',')
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)
    # artist = Artist.query.get(artist_id)
    # serialized_artist = artist.serialized_data
    # form = ArtistForm(obj=artist)
    # form.state.process_data(serialized_artist.get('state'))
    # form.city.process_data(serialized_artist.get('city'))
    # # {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>

    # return render_template('forms/edit_artist.html', form=form, artist=serialized_artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = VenueForm()
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
    flash(f'Artist {artist.name} was listed successfully!')
    return redirect(url_for('show_artist', artist_id=artist_id))

    # if form.validate():
    #     city = City.query.get(form.city.data, form.state.data)
    #     artist.name = form.name.data
    #     artist.city = city
    #     artist.phone = form.phone.data
    #     artist.seeking_venue = form.seeking_venue.data
    #     artist.genres = form.genres.data
    #     artist.image_link = form.image_link.data
    #     artist.facebook_link = form.facebook_link.data
    #     artist.website = form.website.data
    #     artist.seeking_description = form.seeking_description.data

    #     try:
    #         db.session.commit()
    #         flash(f'Artist {artist.name} was listed successfully!')
    #     except:
    #         db.session.rollback()
    #         flash(
    #             f'An error happened. Artist {artist.name} was not listed.')
    #     finally:
    #         db.session.close()

    #     return redirect(url_for('show_artist', artist_id=artist_id))

    # errors = form.errors

    # flash('These Errors happened while creating Venue')
    # for key in errors.keys():
    #     error = errors[key]
    #     flash(f'{key}: f{error}')

    # return edit_artist(artist_id)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue.genres = venue.genres.split(',')
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    return render_template('forms/edit_venue.html', form=form, venue=venue)
    # serialized_venue = venue.serialized_data
    # form = VenueForm(obj=venue)
    # form.state.process_data(serialized_venue.get('state'))
    # form.city.process_data(serialized_venue.get('city'))

    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>

    # return render_template('forms/edit_venue.html', form=form, venue=serialized_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if form.validate():
        city = City.query.get(form.city.data, form.state.data)
        venue.phone = form.phone.data
        venue.name = form.name.data
        venue.city_id = city
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.seeking_description = form.seeking_description.data
        venue.address = form.address.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.genres = form.genres.data

        try:
            db.session.commit()
            flash(f'Venue {venue.name} was listed successfully!')
        except:
            db.session.rollback()
            flash(
                f'An error happened. Venue {venue.name} was not be listed.')
        finally:
            db.session.close()

        return redirect(url_for('show_venue', venue_id=venue_id))

    errors = form.errors

    flash('Below Errors Occurred while creating Venue')
    for key in errors.keys():
        error = errors[key]
        flash(f'{key}: f{error}')

    return edit_venue(venue_id)

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form = ArtistForm()
    if form.validate():
        city = City.query.get(form.city.data, form.state.data)
        artist = Artist(name=form.name.data, city_id=city,
                        phone=form.phone.data, image_link=form.image_link.data, facebook_link=form.facebook_link.data,
                        website=form.website.data, seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data)
        db.session.add(artist)
        db.session.commit()
        flash(f'Artist {artist.name} was listed successfully!')
        return redirect(url_for('index'))

    # return render_template('pages/home.html')

    # errors = form.errors

    # flash('These Errors happened while creating Artist')
    # for key in errors.keys():
    #     error = errors[key]
    #     flash(f'{key}: f{error}')

    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [show.serialized_data for show in Show.query.all()]
    # data=[{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 5,
    #   "artist_name": "Matt Quevedo",
    #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    form = ShowForm()
    if form.validate():
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )
        try:
            db.session.add(show)
            db.session.commit()
            flash('Show was listed successfully!')
        except:
            db.session.rollback()
            flash(f'An error happened. Show was not listed.')
        finally:
            db.session.close()

        return render_template('pages/home.html')

    flash('These Errors happened while creating Show')

    errors = form.errors

    for key in errors.keys():
        error = errors[key]
        flash(f'{key}: f{error}')

    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
