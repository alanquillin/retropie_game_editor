from os import walk
from os.path import isfile
from os.path import join
from os import remove
from os import rename

from retropie_game_editor import cfg
from retropie_game_editor import systems

import logging
import xmltodict

LOG = logging.getLogger(__name__)

opts = [
    cfg.StrOpt('roms_loc', default='/home/pi/RetroPie/roms',
                help='Games root location'),
    cfg.StrOpt('gamelists_loc', default='/home/pi/.emulationstation/gamelists',
               help='Gamelists root location')
]
CONF = cfg.CONF
CONF.register_opts(opts, 'games')


def list_systems_with_game_count():
    s = {}

    for system, data in systems.SYSTEMS.iteritems():
        games = list_games(system, data)
        name = data['name']
        disp_name = data.get('display_name', name)

        s[system] = dict(name=name,
                         display_name=disp_name,
                         system=system,
                         game_count=len(games))
    return s


def list_games(system, system_data=None, include_game_details=False):
    if not system_data:
        system_data = systems.SYSTEMS[system]

    path = _system_path(system)
    games = _list_games(path, system, system_data)

    if not include_game_details:
        return games

    games_details = _get_system_games_details(system)
    games_details_map = {}
    for game in games:
        game_details = get_game_details(system, game,
                                        games_details=games_details)
        games_details_map[game] = {} if not game_details else game_details

    return games_details_map


def get_game_details(system, game, games_details=None):
    if not games_details:
        games_details = _get_system_games_details(system)

    for g in games_details:
        if g.get('path').endswith(game):
            return g

    return None


def save_game_details(system, game, new_details):
    doc = _get_system_gamelist(system)
    games_details = _get_system_games_details(system, doc=doc)
    game_details = get_game_details(system, game, games_details=games_details)

    game_details.update(new_details)

    xml = xmltodict.unparse(doc, pretty=True).encode('utf-8')

    path = _get_game_list_path(system)
    if isfile(path):
        bk_path = path.replace('gamelist.xml', 'gamelist_bk.xml')
        if isfile(bk_path):
            remove(bk_path)
        rename(path, bk_path)

    with open(path, mode='w') as fd:
        fd.write(xml)


def _get_system_games_details(system, doc=None):
    if doc is None:
        doc = _get_system_gamelist(system)
    gamelist = doc.get('gameList', {})
    if not gamelist:
        return []
    games = gamelist.get('game', [])
    return [] if not games else games


def _get_system_gamelist(system):
    path = _get_game_list_path(system)
    with open(path) as fd:
        doc = xmltodict.parse(fd.read())
    return doc


def _list_games(path, system, system_data):
    games = []
    for _, dirs, files in walk(path):
        games.extend([f for f in files
                      if isfile(join(path, f))
                      and _is_file_valid(f, system, system_data)])
        for dir in dirs:
            games.extend(_list_games(join(path, dir), system, system_data))
    return games


def _system_path(system):
    return join(CONF.games.roms_loc, system)


def _is_file_valid(f, system, system_data):
    for ext in system_data.get('supported_exts', [system]):
        if f.endswith(ext):
            return True
    return False


def _get_game_list_path(system):
    return join(join(CONF.games.gamelists_loc, system), 'gamelist.xml')