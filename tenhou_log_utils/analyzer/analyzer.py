from __future__ import absolute_import

import logging

from .components import Game


_LG = logging.getLogger(__name__)


def _process_go(game, data):
    game.set_table(data['table'])
    game.set_config(data['config'])


def _process_agari(game, data):
    game.round.agari(**data)
    game.archive_round()
    if 'result' in data:
        game.set_uma(data['result']['uma'])

def _process_ryuukyoku(game, data):
    game.round.ryuukyoku(**data)
    game.archive_round()
    if 'result' in data:
        game.set_uma(data['result']['uma'])


def _process_node(game, tag, data):
    _LG.debug('%s: %s', tag, data)
    if tag == 'INIT':
        game.init_round(data)
    elif tag == 'DRAW':
        game.round.draw(**data)
    elif tag == 'DISCARD':
        game.round.discard(**data)
    elif tag == 'CALL':
        game.round.call(**data)
    elif tag == 'DORA':
        game.round.state.dora.append(data['hai'])
    elif tag == 'REACH':
        game.round.reach(**data)
    elif tag == 'AGARI':
        _process_agari(game, data)
    elif tag == 'RYUUKYOKU':
        _process_ryuukyoku(game, data)
    elif tag == 'BYE':
        game.round.bye(**data)
    elif tag == 'RESUME':
        game.round.resume(**data)
    else:
        raise NotImplementedError(u'%s: %s' % (tag, data))
    if tag in ['INIT', 'CALL', 'REACH', 'AGARI', 'RYUUKYOKU']:
        _LG.info('%s: %s', tag, data)
        _LG.info(game)


def _analyze_mjlog(game, parsed_log_data):
    # Skip SHUFFLE and TAIKYOKU tag
    _process_go(game, parsed_log_data['meta']['GO'])
    game.init_players(parsed_log_data['meta']['UN'])
    for round_ in parsed_log_data['rounds']:
        for event in round_:
            _process_node(game, event['tag'], event['data'])


def _try_print(game):
    try:
        _LG.info('\n%s', game)
    except Exception:
        pass


def analyze_mjlog(parsed_log_data):
    game = Game()
    try:
        _analyze_mjlog(game, parsed_log_data)
    except Exception as error:
        _try_print(game)
        raise error
