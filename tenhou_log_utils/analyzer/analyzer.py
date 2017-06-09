from __future__ import absolute_import

import logging

from .components import Game


_LG = logging.getLogger(__name__)


def _validate_scores(prev_players, current_players):
    for i, (prev_p, cur_p) in enumerate(zip(prev_players, current_players)):
        if prev_p.score != cur_p.score:
            raise AssertionError(
                'Score from the previous round and the new round is different.'
                ' Player %s; %s (expected: %s)' % (i, prev_p.score, cur_p.score)
            )



def _process_go(game, data):
    _LG.info('Configuring game.')
    game.set_table(data['table'])
    game.set_config(data['config'])


def _process_un(game, data):
    game.init_players(data)


def _process_init(game, data):
    game.init_round(data)
    if game.past_rounds:
        _validate_scores(game.past_rounds[-1].players, game.round.players)

def _process_draw(game, data):
    game.round.draw(**data)


def _process_discard(game, data):
    game.round.discard(**data)


def _process_call(game, data):
    game.round.call(**data)


def _process_dora(game, data):
    game.round.state.dora.append(data['hai'])

def _process_reach(game, data):
    game.round.reach(**data)


def _process_agari(game, data):
    game.round.agari(**data)
    game.archive_round()
    if 'result' in data:
        uma = [res[1] for res in data['result']]
        game.set_uma(uma)


def _process_ryuukyoku(game, data):
    game.round.ryuukyoku(**data)
    game.archive_round()
    if 'result' in data:
        uma = [res[1] for res in data['result']]
        game.set_uma(uma)


def _process_bye(game, data):
    game.round.bye(**data)


def _process_resume(game, data):
    game.round.resume(**data)


def _analyze_mjlog(game, parsed_log_data):
    # Skip SHUFFLE and TAIKYOKU tag
    _process_go(game, parsed_log_data['meta']['GO'])
    _process_un(game, parsed_log_data['meta']['UN'])

    for round_ in parsed_log_data['rounds']:
        for result in round_:
            tag, data = result['tag'], result['data']
            _LG.debug('%s: %s', tag, data)
            if tag == 'INIT':
                _process_init(game, data)
            elif tag == 'DRAW':
                _process_draw(game, data)
            elif tag == 'DISCARD':
                _process_discard(game, data)
            elif tag == 'CALL':
                _process_call(game, data)
            elif tag == 'DORA':
                _process_dora(game, data)
            elif tag == 'REACH':
                _process_reach(game, data)
            elif tag == 'AGARI':
                _process_agari(game, data)
            elif tag == 'RYUUKYOKU':
                _process_ryuukyoku(game, data)
            elif tag == 'BYE':
                _process_bye(game, data)
            elif tag == 'RESUME':
                _process_resume(game, data)
            else:
                raise NotImplementedError('%s: %s' % (tag, data))
            if tag in ['INIT', 'CALL', 'REACH', 'AGARI', 'RYUUKYOKU']:
                _LG.info('%s: %s', tag, data)
                _LG.info(game)


def analyze_mjlog(parsed_log_data):
    game = Game()
    try:
        _analyze_mjlog(game, parsed_log_data)
    except Exception as error:
        _LG.error('\n%s', game.round)
        raise error
