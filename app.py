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
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


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
        "website": artist.website_link,
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

    form = ArtistForm(request.form)
    # if form.validate():
    try:
        artist = Artist(
            name=form.name.data,
            genres=form.genres.data,
            city=form.city.data,
            phone=form.phone.data,
            state=form.state.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            facebook_link=form.facebook_link.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was listed successfully!')
    except:
        db.session.rollback()
        flash('Artist ' + request.form['name'] +
              ' was not listed!')
    finally:
        db.session.close()

    return render_template('pages/home.html')

    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = db.session.query(Show).join(Artist).join(Venue).all()

    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)

    # TODO: replace with real venues data.


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()

    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    form = ShowForm(request.form)

    # if form.validate():
    try:
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = form.start_time.data
        new_show = Show(artist_id=artist_id,
                        venue_id=venue_id, start_time=start_time)
        print('NewHOWWWWW', new_show)
        db.session.add(new_show)
        db.session.commit()
        flash(f'Show {new_show.artist_id} was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            f'An error happened. Show {new_show.artist_id} was not be listed.')
    finally:
        db.session.close()
    # else:
    #     flash('An error happened. Show could not be listed.')

    return render_template('pages/home.html')

    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # return render_template('forms/new_show.html', form=form)


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
