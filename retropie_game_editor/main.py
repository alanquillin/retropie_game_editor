from retropie_game_editor.app import app

from retropie_game_editor import routes
from retropie_game_editor import rest

from retropie_game_editor import cfg
from retropie_game_editor import log

import logging

LOG = logging.getLogger(__name__)

opts = [
    cfg.BoolOpt('debug', default=False,
                help='Enables debug mode for the flask rest api'),
    cfg.IntOpt('port', default=8080, help='Http port of the webserver')
]
CONF = cfg.CONF
CONF.register_opts(opts, 'rest_api')
CONF = cfg.CONF


def init():
    try:
        CONF(project='Retropie Editor')
    except cfg.RequiredOptError:
        CONF.print_help()
        raise SystemExit(1)

    log.init_log()


if __name__ == '__main__':
    init()
    app.run()
