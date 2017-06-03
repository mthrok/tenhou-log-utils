from __future__ import division

import gzip
import logging
import xml.etree.ElementTree as ET

from tenhou_log_utils.mjlog_parser import parse_node

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
def _print_shuffle(result):
    _LG.info('Shuffle:')
    _LG.info('  Seed: %s', result['seed'])
    _LG.info('  Ref: %s', result['ref'])


################################################################################
def _print_go(result):
    _LG.info('Lobby%s:', '' if result['num'] < 0 else ' %s' % result['num'])
    for key, value in result['type'].items():
        _LG.info('    %s: %s', key, value)


################################################################################
def _print_un(result):
    if len(result) == 1:
        _LG.info(
            'Player %s (%s) has returned to the game.', result[0], result[1])
        return

    _LG.info('Players:')
    for i, user, dan, rate, sex in result:
        _LG.info('  %5s: %3s, %8s, %3s, %s', i, dan, rate, sex, user)


################################################################################
def _print_taikyoku(result):
    _LG.info('Dealer: %s', result['oya'])


################################################################################
def _print_scores(scores):
    for i, score in enumerate(scores):
        _LG.info('  %5s: %4s00', i, score)


def _print_init(result):
    _LG.info('=' * 40)
    _LG.info('Initial Game State:')
    _LG.info('  Round: %s', result['round'])
    _LG.info('  Combo: %s', result['combo'])
    _LG.info('  Reach: %s', result['reach'])
    _LG.info('  Dice 1: %s', result['dice1'])
    _LG.info('  Dice 2: %s', result['dice2'])
    _LG.info('  Dora Indicator: %s', _print_hand([result['dora_indicator']]))
    _LG.info('Initial Scores:')
    _print_scores(result['scores'])
    _LG.info('Dealer: %s', result['oya'])
    _LG.info('Initial Hands:')
    for i, hand in enumerate(result['hands']):
        _LG.info('  %5s: %s', i, _print_hand(hand))


################################################################################
def _print_draw(result):
    tile = _tile2unicode(result['tile'])
    _LG.info('Player %s: Draw    %s', result['player'], tile)


################################################################################
def _print_discard(result):
    tile = _tile2unicode(result['tile'])
    _LG.info('Player %s: Discard %s', result['player'], tile)


################################################################################
def _print_call(result):
    tiles = u''.join([_tile2unicode(tile) for tile in result['mentsu']])
    if result['player'] == result['from']:
        from_ = u''
    else:
        from_ = u'from player {}'.format(result['from'])
    _LG.info(
        u'Player %s: %s %s: %s', result['player'], result['type'], from_, tiles)


################################################################################
def _print_reach(result):
    if result['step'] == 1:
        _LG.info(u'Player %s: Reach', result['player'])
    elif result['step'] == 2:
        _LG.info(u'Player %s made deposite.', result['player'])
        if 'ten' in result:
            _LG.info(u'New scores:')
            _print_scores(result['ten'])
    else:
        raise NotImplementedError('Unexpected step value: {}'.format(result))


################################################################################
def _print_ba(ba):
    _LG.info('  Ten-bou:')
    _LG.info('    Combo: %s', ba[0])
    _LG.info('    Riichi: %s', ba[1])


def _print_final_scores(final_scores):
    _LG.info('  Final scores:')
    for score, uma in final_scores:
        _LG.info('    %4s00: %5s', int(score), uma)


def _print_agari(result):
    limit = [
        'No limit',
        'Mangan',
        'Haneman',
        'Baiman',
        'Sanbaiman',
        'Yakuman',
    ]

    yaku_name = [
        'tsumo',
        'riichi',
        'ippatsu',
        'chankan',
        'rinshan',
        'haitei',
        'houtei',
        'pinfu',
        'tanyao',
        'ippeiko',
        'ji_fan_ton',
        'ji_fan_nan',
        'ji_fan_sha',
        'ji_fan_pe',
        'ba_fan_ton',
        'ba_fan_nan',
        'ba_fan_sha',
        'ba_fan_pe',
        'yakuhai_haku',
        'yakuhai_hatsu',
        'yakuhai_chun',
        'daburi',
        'chiitoi',
        'chanta',
        'itsuu',
        'sanshokudoujin',
        'sanshokudou',
        'sankantsu',
        'toitoi',
        'sanankou',
        'shousangen',
        'honrouto',
        'ryanpeikou',
        'junchan',
        'honitsu',
        'chinitsu',

        'renhou',
        'tenhou',
        'chihou',
        'daisangen',
        'suuankou',
        'suuankou_tanki',
        'tsuiisou',
        'ryuuiisou',
        'chinrouto',
        'chuurenpoutou',
        'junsei_chuurenpoutou',
        'kokushi',
        'kokushi_13',
        'daisuushi',
        'shousuushi',
        'suukantsu',

        'dora',
        'uradora',
        'akadora',
    ]
    _LG.info('Player %s wins.', result['player'])
    if result['player'] == result['from']:
        _LG.info('  Tsumo.')
    else:
        _LG.info('  Ron from player %s', result['from'])
    _LG.info('  Hand: %s', _print_hand(result['hand']))
    _LG.info('  Machi: %s', _print_hand(result['machi']))
    _LG.info('  Dora Indicator: %s', _print_hand(result['dora']))
    if result['ura_dora']:
        _LG.info('  Ura Dora: %s', _print_hand(result['ura_dora']))
    _LG.info('  Yaku:')
    for yaku, han in result['yaku']:
        _LG.info('      %s (%s): %s [Han]', yaku_name[yaku], yaku, han)
    if result['yakuman']:
        for yaku in result['yakuman']:
            _LG.info('      %s (%s)', yaku_name[yaku], yaku)
    _LG.info('  Fu: %s', result['ten'][0])
    _LG.info('  Score: %s', result['ten'][1])
    if result['ten'][2]:
        _LG.info('    - %s', limit[result['ten'][2]])
    _print_ba(result['ba'])
    _LG.info('  Scores:')
    for cur, def_ in result['scores']:
        _LG.info('    %4s00: %5s', cur, def_)

    if 'final_scores' in result:
        _print_final_scores(result['final_scores'])


###############################################################################
def _print_dora(result):
    _LG.info('New Dora Indicator: %s', _print_hand([result['hai']]))


###############################################################################
def _print_ryuukyoku(result):
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
    _LG.info('  Reason: %s', reason[result['type']])
    for i, hand in enumerate(result['hands']):
        _LG.info('Player %s: %s', i, _print_hand(hand))
    for cur, def_ in result['scores']:
        _LG.info('    %s: %s', cur, def_)
    _print_ba(result['ba'])
    if 'final_scores' in result:
        _print_final_scores(result['final_scores'])


################################################################################
def _print_bye(result):
    _LG.info('Player %s has left the game.', result['player'])


################################################################################
def _print_node(tag, result):
    _LG.debug('%s: %s', tag, result)
    if tag == 'GO':
        _print_go(result)
    elif tag == 'UN':
        _print_un(result)
    elif tag == 'TAIKYOKU':
        _print_taikyoku(result)
    elif tag == 'SHUFFLE':
        _print_shuffle(result)
    elif tag == 'INIT':
        _print_init(result)
    elif tag == 'DORA':
        _print_dora(result)
    elif tag == 'DRAW':
        _print_draw(result)
    elif tag == 'DISCARD':
        _print_discard(result)
    elif tag == 'CALL':
        _print_call(result)
    elif tag == 'REACH':
        _print_reach(result)
    elif tag == 'AGARI':
        _print_agari(result)
    elif tag == 'RYUUKYOKU':
        _print_ryuukyoku(result)
    elif tag == 'BYE':
        _print_bye(result)
    else:
        raise NotImplementedError('{}: {}'.format(tag, result))


################################################################################
def _load_gzipped(filepath):
    with gzip.open(filepath) as file_:
        return ET.parse(file_)


def main(filepath):
    """Entry point for `view` command."""
    obj = _load_gzipped(filepath) if '.gz' in filepath else ET.parse(filepath)
    for node in obj.getroot():
        result = parse_node(node.tag, node.attrib)
        _print_node(result['tag'], result['result'])
