import requests
import xmltodict


class TheGamesDBRepo(object):
    _base_url = 'http://thegamesdb.net/api'

    def get_games_list(self, **kwargs):
        self._validate_and_sanitize_input(kwargs, req_all=['name'])

        url = '%s/GetGamesList.php' % self._base_url
        r = requests.get(url, params=kwargs)

        root = xmltodict.parse(r.content)
        doc = root['Data']
        return doc.get('Game')

    def get_game(self, **kwargs):
        self._validate_and_sanitize_input(kwargs, req_one=['name', 'id',
                                                           'exactname'])

        url = '%s/GetGame.php' % self._base_url
        r = requests.get(url, params=kwargs)

        root = xmltodict.parse(r.content)
        doc = root['Data']
        return doc.get('Game')

    @staticmethod
    def _validate_and_sanitize_input(input, req_one=None, req_all=None):
        if 'system' in input and 'platform' not in input:
            system = input.pop('system')
            input['platform'] = system

        if req_one:
            valid = False
            for r in req_one:
                if r in input:
                    valid = True
                    break
            if not valid:
                raise ValueError('At least one of the following parameter '
                                 'is required. [%s]', ', '.join(req_one))

        if req_all:
            missing = []
            for r in req_all:
                if r not in input:
                    missing.append(r)
            if missing:
                raise ValueError('The following parameters are required but '
                                 'were not provided. [%s]',
                                 ', '.join(missing))
