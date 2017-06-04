from __future__ import division
from __future__ import absolute_import

import logging

from tenhou_log_utils.parser import parse_node

_LG = logging.getLogger(__name__)


def _tile2unicode(tile):
    tile_unicodes = [
        u'\U0001f010',
        u'\U0001f011',
        u'\U0001f012',
        u'\U0001f013',
        u'\U0001f014',
        u'\U0001f015',
        u'\U0001f016',
        u'\U0001f017',
        u'\U0001f018',
        u'\U0001f019',
        u'\U0001f01a',
        u'\U0001f01b',
        u'\U0001f01c',
        u'\U0001f01d',
        u'\U0001f01e',
        u'\U0001f01f',
        u'\U0001f020',
        u'\U0001f021',
        u'\U0001f007',
        u'\U0001f008',
        u'\U0001f009',
        u'\U0001f00a',
        u'\U0001f00b',
        u'\U0001f00c',
        u'\U0001f00d',
        u'\U0001f00e',
        u'\U0001f00f',
        u'\U0001f000',
        u'\U0001f001',
        u'\U0001f002',
        u'\U0001f003',
        u'\U0001f006',
        u'\U0001f005',
        u'\U0001f004',
    ]
    return u'{} {}'.format(tile_unicodes[tile//4], tile % 4)


def _print_hand(tiles):
    tiles.sort()
    return u' '.join([_tile2unicode(tile) for tile in tiles])


################################################################################
def _print_shuffle(data):
    _LG.info('Shuffle:')
    _LG.info('  Seed: %s', data['seed'])
    _LG.info('  Ref: %s', data['ref'])


################################################################################
def _print_go(data):
    _LG.info('Lobby%s:', '' if data['num'] < 0 else ' %s' % data['num'])
    for key, value in data['mode'].items():
        _LG.info('    %s: %s', key, value)


################################################################################
def _print_un(data):
    if len(data) == 1:
        index, name = data[0]['index'], data[0]['name']
        _LG.info('Player %s (%s) has returned to the game.', index, name)
        return

    _LG.info('Players:')
    _LG.info('  %5s: %3s, %8s, %3s, %s', 'Index', 'Dan', 'Rate', 'Sex', 'Name')
    for datum in data:
        index, name = datum['index'], datum['name']
        dan, rate, sex = datum['dan'], datum['rate'], datum['sex']
        _LG.info('  %5s: %3s, %8.2f, %3s, %s', index, dan, rate, sex, name)


################################################################################
def _print_taikyoku(data):
    _LG.info('Dealer: %s', data['oya'])


################################################################################
def _print_scores(scores):
    for i, score in enumerate(scores):
        _LG.info('  %5s: %4s00', i, score)


def _print_init(data):
    _LG.info('=' * 40)
    _LG.info('Initial Game State:')
    _LG.info('  Round: %s', data['round'])
    _LG.info('  Combo: %s', data['combo'])
    _LG.info('  Reach: %s', data['reach'])
    _LG.info('  Dice 1: %s', data['dice1'])
    _LG.info('  Dice 2: %s', data['dice2'])
    _LG.info('  Dora Indicator: %s', _print_hand([data['dora_indicator']]))
    _LG.info('Initial Scores:')
    _print_scores(data['scores'])
    _LG.info('Dealer: %s', data['oya'])
    _LG.info('Initial Hands:')
    for i, hand in enumerate(data['hands']):
        _LG.info('  %5s: %s', i, _print_hand(hand))


################################################################################
def _print_draw(data):
    tile = _tile2unicode(data['tile'])
    _LG.info('Player %s: Draw    %s', data['player'], tile)


################################################################################
def _print_discard(data):
    tile = _tile2unicode(data['tile'])
    _LG.info('Player %s: Discard %s', data['player'], tile)


################################################################################
def _print_call(data):
    tiles = u''.join([_tile2unicode(tile) for tile in data['mentsu']])
    if data['player'] == data['from']:
        from_ = u''
    else:
        from_ = u'from player {}'.format(data['from'])
    _LG.info(
        u'Player %s: %s %s: %s', data['player'], data['type'], from_, tiles)


################################################################################
def _print_reach(data):
    if data['step'] == 1:
        _LG.info(u'Player %s: Reach', data['player'])
    elif data['step'] == 2:
        _LG.info(u'Player %s made deposite.', data['player'])
        if 'ten' in data:
            _LG.info(u'New scores:')
            _print_scores(data['ten'])
    else:
        raise NotImplementedError('Unexpected step value: {}'.format(data))


################################################################################
def _print_ba(ba):
    _LG.info('  Ten-bou:')
    _LG.info('    Combo: %s', ba[0])
    _LG.info('    Riichi: %s', ba[1])


def _print_final_scores(final_scores):
    _LG.info('  Final scores:')
    for score, uma in final_scores:
        _LG.info('    %4s00: %5s', int(score), uma)


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
    _LG.info('Player %s wins.', data['player'])
    if data['player'] == data['from']:
        _LG.info('  Tsumo.')
    else:
        _LG.info('  Ron from player %s', data['from'])
    _LG.info('  Hand: %s', _print_hand(data['hand']))
    _LG.info('  Machi: %s', _print_hand(data['machi']))
    _LG.info('  Dora Indicator: %s', _print_hand(data['dora']))
    if data['ura_dora']:
        _LG.info('  Ura Dora: %s', _print_hand(data['ura_dora']))
    _LG.info('  Yaku:')
    for yaku, han in data['yaku']:
        _LG.info('      %s (%s): %s [Han]', yaku_name[yaku], yaku, han)
    if data['yakuman']:
        for yaku in data['yakuman']:
            _LG.info('      %s (%s)', yaku_name[yaku], yaku)
    _LG.info('  Fu: %s', data['ten'][0])
    _LG.info('  Score: %s', data['ten'][1])
    if data['ten'][2]:
        _LG.info('    - %s', limit[data['ten'][2]])
    _print_ba(data['ba'])
    _LG.info('  Scores:')
    for cur, def_ in data['scores']:
        _LG.info('    %4s00: %5s', cur, def_)

    if 'final_scores' in data:
        _print_final_scores(data['final_scores'])


###############################################################################
def _print_dora(data):
    _LG.info('New Dora Indicator: %s', _print_hand([data['hai']]))


###############################################################################
def _print_ryuukyoku(data):
    reason = {
        'nm': 'Nagashi Mangan',
        'yao9': '9-Shu 9-Hai',
        'kaze4': '4 Fu',
        'reach4': '4 Reach',
        'ron3': '3 Ron',
        'kan4': '4 Kan',
        'out': 'Out of tile'
    }

    _LG.info('Ryukyoku:')
    _LG.info('  Reason: %s', reason[data['type']])
    for i, hand in enumerate(data['hands']):
        _LG.info('Player %s: %s', i, _print_hand(hand))
    for cur, def_ in data['scores']:
        _LG.info('    %s: %s', cur, def_)
    _print_ba(data['ba'])
    if 'final_scores' in data:
        _print_final_scores(data['final_scores'])


################################################################################
def _print_bye(data):
    _LG.info('Player %s has left the game.', data['player'])


################################################################################
def _print_node(tag, data):
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
        _print_call(data)
    elif tag == 'REACH':
        _print_reach(data)
    elif tag == 'AGARI':
        _print_agari(data)
    elif tag == 'RYUUKYOKU':
        _print_ryuukyoku(data)
    elif tag == 'BYE':
        _print_bye(data)
    else:
        raise NotImplementedError('{}: {}'.format(tag, data))


################################################################################
def view_mjlog(filepath):
    """Entry point for `view` command."""
    from tenhou_log_utils.io import load_mjlog
    for node in load_mjlog(filepath):
        result = parse_node(node.tag, node.attrib)
        _print_node(result['tag'], result['data'])
