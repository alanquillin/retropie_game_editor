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


@app.route('/tools')
def tools_dashboard():
    games_repo.list_systems_with_game_count()
    return render_template('tools.html')
