from retropie_game_editor.app import app
from retropie_game_editor.repos import games_repo
from retropie_game_editor.repos import images_repo

from flask import jsonify
from flask import render_template
from flask import request
from flask import send_file

from datetime import datetime
from HTMLParser import HTMLParser
import logging
import urllib

LOG = logging.getLogger(__name__)


@app.errorhandler(404)
def page_not_found(*args, **kwargs):
    return render_template('errors/404.html'), 404


@app.route('/')
def dashboard():
    systems = games_repo.list_systems_with_game_count()
    return render_template('dashboard.html', systems=systems)


@app.route('/systems')
def list_systems():
    content_type = request.headers.get('Content-Type')
    systems = games_repo.list_systems_with_game_count()

    if content_type == 'application/json':
        return jsonify(systems)


@app.route('/systems/<system>/games')
def list_system_games(system):
    content_type = request.headers.get('Content-Type')
    games_details = games_repo.list_games(system, include_game_details=True)

    if content_type == 'application/json':
        return jsonify(games_details)

    return render_template('partials/games/list.html', system=system,
                           games_details=games_details)


@app.route('/systems/<system>/games/<game>', methods=['GET', 'POST'])
def game_details(system, game):
    game = _clean_game(game)
    if request.method == 'POST':
        game_details = games_repo.get_game_details(system, game)
        form = request.form
        release_date_f = form['releaseDate']
        release_date = datetime.strptime(release_date_f, '%m/%d/%Y')

        data = dict(name=form['name'],
                    path=form['path'],
                    developer=form['developer'],
                    publisher=form['publisher'],
                    genre=form['genre'],
                    releasedate=release_date.strftime('%Y%m%dT000000'),
                    players=form['players'],
                    desc=form['description'])
        if game_details is None:
            LOG.debug('Not data found fo game...')
            changed = True
        else:
            LOG.debug('Checking if any game data has changed...')
            changed = False
            for k, v in game_details.iteritems():
                if k not in ('name', 'path', 'developer', 'publisher',
                             'genre', 'releasedate', 'players', 'desc'):
                    continue
                if data.get(k) != v:
                    LOG.info('Key \'%s\' has changed.  Old value: %s, '
                             'New value: %s', k, v, data.get(k))
                    changed = True
                    break
        if changed:
            LOG.debug('Game details changed, saving updated data...')
            games_repo.save_game_details(system, game, data)
        else:
            LOG.debug('Game details did not change, nothing to do!')

    game_details = games_repo.get_game_details(system, game)
    if game_details is None:
        game_details = dict(path='./%s' % game)

    if game_details.get('releasedate'):
        rd = datetime.strptime(game_details.get('releasedate'), '%Y%m%dT%H%M%S')
        game_details['releasedate_display'] = rd.strftime('%m/%d/%Y')
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        return jsonify(game_details)

    return render_template('partials/games/details.html', game=game,
                           game_details=game_details, system=system)


@app.route('/systems/<system>/games/<game>/image')
def get_game_image(system, game):
    game = _clean_game(game)
    image_path = images_repo.get_game_image(system, game)

    if not image_path:
        return render_template('errors/404.html'), 404

    return send_file(image_path, mimetype='image/jpeg')


@app.route('/systems/<system>/games/<game>/image/thumbnail')
def get_game_image_thumbnail(system, game):
    game = _clean_game(game)
    image_path = images_repo.get_game_image_thumbnail(system, game)

    if not image_path:
        return render_template('errors/404.html'), 404

    return send_file(image_path, mimetype='image/jpeg')


def _clean_game(game):
    h = HTMLParser()
    game = h.unescape(game)
    game = urllib.unquote(game).decode('utf8')
    game = game.replace('+', ' ')
    return game
