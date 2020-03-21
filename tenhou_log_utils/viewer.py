"""Functions for parsing mjlog data"""
from __future__ import division
from __future__ import absolute_import

import logging

_LG = logging.getLogger(__name__)


def _tile2unicode(tile):
    tile_unicodes = [
        # M
        u'\U0001f007',
        u'\U0001f008',
        u'\U0001f009',
        u'\U0001f00a',
        u'\U0001f00b',
        u'\U0001f00c',
        u'\U0001f00d',
        u'\U0001f00e',
        u'\U0001f00f',
        # P
        u'\U0001f019',
        u'\U0001f01a',
        u'\U0001f01b',
        u'\U0001f01c',
        u'\U0001f01d',
        u'\U0001f01e',
        u'\U0001f01f',
        u'\U0001f020',
        u'\U0001f021',
        # S
        u'\U0001f010',
        u'\U0001f011',
        u'\U0001f012',
        u'\U0001f013',
        u'\U0001f014',
        u'\U0001f015',
        u'\U0001f016',
        u'\U0001f017',
        u'\U0001f018',
        # Z
        u'\U0001f000',
        u'\U0001f001',
        u'\U0001f002',
        u'\U0001f003',
        u'\U0001f006',
        u'\U0001f005',
        u'\U0001f004',
    ]
    return u'{} {}'.format(tile_unicodes[tile//4], tile % 4)


def convert_hand(tiles):
    """Convert hands (int) into unicode characters for print."""
    return u' '.join([_tile2unicode(tile) for tile in tiles])


################################################################################
def _print_shuffle(data):
    _LG.info('Shuffle:')
    _LG.info('  Seed: %s', data['seed'])
    _LG.info('  Ref: %s', data['ref'])


################################################################################
def _print_go(data):
    _LG.info('Lobby%s:', '' if data['lobby'] < 0 else ' %s' % data['lobby'])
    _LG.info('  Table: %s', data['table'])
    for key, value in data['config'].items():
        _LG.info('    %s: %s', key, value)


################################################################################
def _print_resume(data):
    index, name = data['index'], data['name']
    _LG.info('Player %s (%s) has returned to the game.', index, name)


def _print_un(data):
    _LG.info('Players:')
    _LG.info('  %5s: %3s, %8s, %3s, %s', 'Index', 'Dan', 'Rate', 'Sex', 'Name')
    for i, datum in enumerate(data):
        dan, rate = datum['dan'], datum['rate']
        name, sex = datum['name'], datum['sex']
        _LG.info('  %5s: %3s, %8.2f, %3s, %s', i, dan, rate, sex, name)


################################################################################
def _print_taikyoku(data):
    _LG.info('Dealer: %s', data['oya'])


################################################################################
def _print_scores(scores):
    for i, score in enumerate(scores):
        _LG.info('  %6s: %6s', i, score)


def _print_init(data):
    dora = convert_hand([data['dora']])
    field_ = data['round'] // 4
    repeat = field_ // 4
    round_ = data['round'] % 4 + 1
    field = ['Ton', 'Nan', 'Xia', 'Pei'][field_ % 4]
    _LG.info('Initial Game State:')
    if repeat:
        _LG.info('  Round: %s %s %s Kyoku', repeat, field, round_)
    else:
        _LG.info('  Round: %s %s Kyoku', field, round_)
    _LG.info('  Combo: %s', data['combo'])
    _LG.info('  Reach: %s', data['reach'])
    _LG.info('  Dice 1: %s', data['dices'][0])
    _LG.info('  Dice 2: %s', data['dices'][1])
    _LG.info('  Dora Indicator: %s', dora)
    _LG.info('  Initial Scores:')
    _print_scores(data['scores'])
    _LG.info('  Dealer: %s', data['oya'])
    _LG.info('  Initial Hands:')
    for i, hand in enumerate(data['hands']):
        _LG.info('  %5s: %s', i, convert_hand(sorted(hand)))


################################################################################
def _print_draw(data):
    tile = _tile2unicode(data['tile'])
    _LG.info('Player %s: Draw    %s', data['player'], tile)


################################################################################
def _print_discard(data):
    tile = _tile2unicode(data['tile'])
    _LG.info('Player %s: Discard %s', data['player'], tile)


################################################################################
def _print_call(caller, callee, call_type, mentsu):
    tiles = u''.join([_tile2unicode(tile) for tile in mentsu])
    if call_type == 'KaKan' or caller == callee:
        from_ = u''
    else:
        from_ = u' from player {}'.format(callee)
    _LG.info(u'Player %s: %s%s: %s', caller, call_type, from_, tiles)


################################################################################
def _print_reach(data):
    if data['step'] == 1:
        _LG.info(u'Player %s: Reach', data['player'])
    elif data['step'] == 2:
        _LG.info(u'Player %s made deposite.', data['player'])
        if 'scores' in data:
            _LG.info(u'New scores:')
            _print_scores(data['scores'])
    else:
        raise NotImplementedError('Unexpected step value: {}'.format(data))


################################################################################
def _print_ba(ba):
    _LG.info('  Ten-bou:')
    _LG.info('    Combo: %s', ba['combo'])
    _LG.info('    Reach: %s', ba['reach'])


def _print_result(result):
    _LG.info('  Result:')
    for score, uma in zip(result['scores'], result['uma']):
        _LG.info('    %6s: %6s', score, uma)


def _print_agari(data):
    limit = [
        'No limit',
        'Mangan',
        'Haneman',
        'Baiman',
        'Sanbaiman',
        'Yakuman',
    ]

    yaku_name = [
        # 1 han
        'Tsumo',
        'Reach',
        'Ippatsu',
        'Chankan',
        'Rinshan-kaihou',
        'Hai-tei-rao-yue',
        'Hou-tei-rao-yui',
        'Pin-fu',
        'Tan-yao-chu',
        'Ii-pei-ko',
        # Ji-kaze
        'Ton',
        'Nan',
        'Xia',
        'Pei',
        # Ba-kaze
        'Ton',
        'Nan',
        'Xia',
        'Pei',
        'Haku',
        'Hatsu',
        'Chun',
        # 2 han
        'Double reach',
        'Chii-toi-tsu',
        'Chanta',
        'Ikki-tsuukan',
        'San-shoku-dou-jun',
        'San-shoku-dou-kou',
        'San-kan-tsu',
        'Toi-Toi-hou',
        'San-ankou',
        'Shou-sangen',
        'Hon-rou-tou',
        # 3 han
        'Ryan-pei-kou',
        'Junchan',
        'Hon-itsu',
        # 6 han
        'Chin-itsu',
        # mangan
        'Ren-hou',
        # yakuman
        'Ten-hou',
        'Chi-hou',
        'Dai-sangen',
        'Suu-ankou',
        'Suu-ankou Tanki',
        'Tsu-iisou',
        'Ryu-iisou',
        'Chin-routo',
        'Chuuren-poutou',
        'Jyunsei Chuuren-poutou 9',
        'Kokushi-musou',
        'Kokushi-musou 13',
        'Dai-suushi',
        'Shou-suushi',
        'Su-kantsu',
        # kensyou
        'Dora',
        'Ura-dora',
        'Aka-dora',
    ]
    _LG.info('Player %s wins.', data['winner'])
    if 'loser' in data:
        _LG.info('  Ron from player %s', data['loser'])
    else:
        _LG.info('  Tsumo.')
    _LG.info('  Hand: %s', convert_hand(sorted(data['hand'])))
    _LG.info('  Machi: %s', convert_hand(data['machi']))
    _LG.info('  Dora Indicator: %s', convert_hand(data['dora']))
    if data['ura_dora']:
        _LG.info('  Ura Dora: %s', convert_hand(data['ura_dora']))
    _LG.info('  Yaku:')
    for yaku, han in data['yaku']:
        _LG.info('      %-20s (%2d): %2d [Han]', yaku_name[yaku], yaku, han)
    if data['yakuman']:
        for yaku in data['yakuman']:
            _LG.info('      %s (%s)', yaku_name[yaku], yaku)
    _LG.info('  Fu: %s', data['ten']['fu'])
    _LG.info('  Score: %s', data['ten']['point'])
    if data['ten']['limit']:
        _LG.info('    - %s', limit[data['ten']['limit']])
    _print_ba(data['ba'])
    _LG.info('  Scores:')
    for cur, gain in zip(data['scores'], data['gains']):
        _LG.info('    %6s: %6s', cur, gain)

    if 'result' in data:
        _print_result(data['result'])


###############################################################################
def _print_dora(data):
    _LG.info('New Dora Indicator: %s', convert_hand([data['hai']]))


###############################################################################
def _print_ryuukyoku(data):
    reason = {
        'nm': 'Nagashi Mangan',
        'yao9': '9-Shu 9-Hai',
        'kaze4': '4 Fu',
        'reach4': '4 Reach',
        'ron3': '3 Ron',
        'kan4': '4 Kan',
    }

    _LG.info('Ryukyoku:')
    if 'reason' in data:
        _LG.info('  Reason: %s', reason[data['reason']])
    for i, hand in enumerate(data['hands']):
        if hand is not None:
            _LG.info('Player %s: %s', i, convert_hand(sorted(hand)))
    _LG.info('  Scores:')
    for cur, gain in zip(data['scores'], data['gains']):
        _LG.info('    %6s: %6s', cur, gain)
    _print_ba(data['ba'])
    if 'result' in data:
        _print_result(data['result'])


################################################################################
def _print_bye(data):
    _LG.info('Player %s has left the game.', data['index'])


################################################################################
def print_node(tag, data):
    """Print XML node of tenhou mjlog parsed with `parse_node` function.

    Parameters
    ----------
    tag : str
        Tags such as 'GO', 'DORA', 'AGARI' etc...

    data: dict
        Parsed info of the node
    """
    _LG.debug('%s: %s', tag, data)
    if tag == 'GO':
        _print_go(data)
    elif tag == 'UN':
        _print_un(data)
    elif tag == 'TAIKYOKU':
        _print_taikyoku(data)
    elif tag == 'SHUFFLE':
        _print_shuffle(data)
    elif tag == 'INIT':
        _print_init(data)
    elif tag == 'DORA':
        _print_dora(data)
    elif tag == 'DRAW':
        _print_draw(data)
    elif tag == 'DISCARD':
        _print_discard(data)
    elif tag == 'CALL':
        _print_call(**data)
    elif tag == 'REACH':
        _print_reach(data)
    elif tag == 'AGARI':
        _print_agari(data)
    elif tag == 'RYUUKYOKU':
        _print_ryuukyoku(data)
    elif tag == 'BYE':
        _print_bye(data)
    elif tag == 'RESUME':
        _print_resume(data)
    else:
        raise NotImplementedError('{}: {}'.format(tag, data))
