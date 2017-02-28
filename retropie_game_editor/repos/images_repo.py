from retropie_game_editor.repos import games_repo
from retropie_game_editor import cfg
from flask import send_file
from PIL import Image
import logging
from os import makedirs
from os.path import isfile
from os.path import isdir
from os.path import join
from os.path import split
from os import remove

LOG = logging.getLogger(__name__)
opts = [
    cfg.StrOpt('images_loc', default='/home/pi/.emulationstation/downloaded_images',
               help='Games images root location'),
    cfg.StrOpt('thumbnails_loc', default='/home/pi/.emulationstation/image_thumbnails',
               help='Games images thumbnail root location'),
    cfg.IntOpt('thumbnail_width', default=240)
]
CONF = cfg.CONF
CONF.register_opts(opts, 'games')


def get_game_image(system, game):
    game_details = games_repo.get_game_details(system, game)

    if not game_details:
        return None

    full_orig_image_path = game_details.get('image')

    orig_path, orig_filename = split(full_orig_image_path)
    actual_path = join(join(CONF.games.images_loc, system), orig_filename)

    return actual_path


def get_game_image_thumbnail(system, game):
    actual_path_full = get_game_image(system, game)

    if not actual_path_full:
        return None

    actual_path, actual_filename = split(actual_path_full)
    thumbnail_filename = actual_filename.replace('.jpg', '-thumbnail.jpg')
    thumbnail_system_path = join(CONF.games.thumbnails_loc, system)
    thumbnail_path = join(thumbnail_system_path, thumbnail_filename)

    if not isfile(thumbnail_path):
        LOG.debug('Thumbnail %s does not exist.  Creating...', thumbnail_path)
        if not isdir(thumbnail_system_path):
            makedirs(thumbnail_system_path)
        _create_thumbnail(actual_path_full, thumbnail_path)
    else:
        LOG.debug('Thumbnail %s already exists.', thumbnail_path)
        img = Image.open(thumbnail_path)
        if img.width != CONF.games.thumbnail_width:
            LOG.debug('Thumbnail does not have the correct dimensions, '
                      'recreating...')
            remove(thumbnail_path)
            _create_thumbnail(actual_path_full, thumbnail_path)

    return send_file(thumbnail_path, mimetype='image/jpeg')


def _create_thumbnail(orig_path, thumbnail_path):
    img = Image.open(orig_path)
    mult = float(CONF.games.thumbnail_width) / img.width
    height = img.height * mult
    size = (CONF.games.thumbnail_width, int(round(height)))
    img.resize(size).save(thumbnail_path)