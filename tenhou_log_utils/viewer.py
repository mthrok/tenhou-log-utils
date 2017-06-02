from __future__ import division

import logging
import xml.etree.ElementTree as ET

_LG = logging.getLogger(__name__)


def _unquote(quoted):
    try:
        from urllib.parse import unquote
        return unquote(quoted)
    except ImportError:
        from urllib2 import unquote
        return unquote(quoted).decode('utf-8')


def _parse_int_list(val):
    if val:
        return [int(val) for val in val.split(',')]
    return []


def _parse_float_list(val):
    if val:
        return [float(val) for val in val.split(',')]
    return []


def _parse_lobby_type(lobby_type):
    return {
        'human': lobby_type & 0x01,
        'no-red': (lobby_type & 0x02) >> 1,
        'no-kui': (lobby_type & 0x04) >> 2,
        'ton-nan': (lobby_type & 0x08) >> 3,
        'san-mah': (lobby_type & 0x10) >> 4,
        'toku-jou': (lobby_type & 0x20) >> 5,
        'soku': (lobby_type & 0x40) >> 6,
        'jou-kyu': (lobby_type & 0x80) >> 7,
    }


def _parse_lobby(attrib):
    lobby_type = _parse_lobby_type(int(attrib['type']))
    _LG.info('Lobby Type: %s (%s)', attrib['type'], attrib.get('lobby', 'Not Defined'))
    for key, value in lobby_type.items():
        _LG.info('    %s: %s', key, value)


def _parse_player(attrib):
    if len(attrib) == 1:
        index = int(list(attrib.keys())[0][1])
        name = _unquote(list(attrib.values())[0])
        _LG.info('Player %s (%s) has returned to the game.', index, name)
    else:
        users = [attrib[key] for key in ['n0', 'n1', 'n2', 'n3'] if key in attrib]
        dans = attrib['dan'].split(',')
        rates = attrib['rate'].split(',')
        sexes = attrib['sx'].split(',')
        _LG.info('Players:')
        _LG.info('  Index, Dan,     Rate, Sex, Name')
        for i, (user, dan, rate, sex) in enumerate(zip(users, dans, rates, sexes)):
            _LG.info('  %5s: %3s, %8s, %3s, %s', i, dan, rate, sex, _unquote(user))


def _parse_game(attrib):
    _LG.info('Dealer: %s', attrib['oya'])


_TILES = [
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


def _tile2unicode(tile):
    return u'{} {}'.format(_TILES[tile//4], tile % 4)


def _parse_hand(tiles):
    tiles.sort()
    return u' '.join([_tile2unicode(tile) for tile in tiles])


def _parse_initial(attrib):
    seed = _parse_int_list(attrib['seed'])
    n_round, combo, riichi, dice1, dice2, dora_indicator = seed

    _LG.info('=' * 40)
    _LG.info('Initial Game State:')
    _LG.info('  Round: %s', n_round)
    _LG.info('  Combo: %s', combo)
    _LG.info('  Riichi: %s', riichi)
    _LG.info('  Dice 1: %s', dice1)
    _LG.info('  Dice 2: %s', dice2)
    _LG.info('  Dora Indicator: %s', _parse_hand([dora_indicator]))

    scores = [int(score) for score in attrib['ten'].split(',')]
    _LG.info('Initial Scores:')
    for i, score in enumerate(scores):
        _LG.info('  %5s: %s [k]', i, score)
    _LG.info('Dealer: %s', attrib['oya'])

    _LG.info('Initial Hands:')
    hands = [
        _parse_int_list(attrib[key])
        for key in ['hai0', 'hai1', 'hai2', 'hai3'] if key in attrib
    ]
    for i, hand in enumerate(hands):
        _LG.info('  %5s: %s', i, _parse_hand(hand))


def _parse_draw(tag):
    player = ord(tag[0]) - ord('T')
    tile = _tile2unicode(int(tag[1:]))
    _LG.info('Player %s: Draw    %s', player, tile)


def _parse_discard(tag):
    player = ord(tag[0]) - ord('D')
    tile = _tile2unicode(int(tag[1:]))
    _LG.info('Player %s: Discard %s', player, tile)


def _parse_shuntsu(meld):
    t = (meld & 0xfc00) >> 10
    r = t % 3
    t = t // 3
    t = 9 * (t // 7) + (t % 7)
    t *= 4
    h = [
        t + 4*0 + ((meld & 0x0018)>>3),
        t + 4*1 + ((meld & 0x0060)>>5),
        t + 4*2 + ((meld & 0x0180)>>7),
    ]
    if r == 1:
        h = [h[1], h[0], h[2]]
    elif r == 2:
        h = [h[2], h[0], h[1]]
    return h


def _parse_koutsu(meld):
    unused = (meld &0x0060) >> 5
    t = (meld & 0xfe00) >> 9
    r = t % 3
    t = t // 3
    t *= 4
    h = [t, t, t]
    if unused == 0:
        h[0] += 1
        h[1] += 2
        h[2] += 3
    elif unused == 1:
        h[0] += 0
        h[1] += 2
        h[2] += 3
    elif unused == 2:
        h[0] += 0
        h[1] += 1
        h[2] += 3
    elif unused == 3:
        h[0] += 0
        h[1] += 1
        h[2] += 2
    if r == 1:
        h = [h[1], h[0], h[2]]
    elif r == 2:
        h = [h[2], h[0], h[1]]
    kui = meld & 0x3
    if kui < 3:
        h = [h[2], h[0], h[1]]
    if kui < 2:
        h = [h[2], h[0], h[1]]
    return h


def _parse_chankan(meld):
    added = (meld & 0x0060) >> 5
    t = (meld & 0xFE00) >> 9
    r = t % 3
    t = t // 3
    t *= 4
    h = [t, t, t]
    if added == 0:
        h[0] += 1
        h[1] += 2
        h[2] += 3
    elif added == 1:
        h[0] += 0
        h[1] += 2
        h[2] += 3
    elif added == 2:
        h[0] += 0
        h[1] += 1
        h[2] += 3
    elif added == 3:
        h[0] += 0
        h[1] += 1
        h[2] += 2
    if r == 1:
        h = [h[1], h[0], h[2]]
    elif r == 2:
        h = [h[2], h[0], h[1]]
    kui = meld & 0x3
    if kui == 3:
        h = [t + added, h[0], h[1], h[2]]
    elif kui == 2:
        h = [h[1], t + added, h[0], h[2]]
    elif kui == 1:
        h = [h[2], h[1], t + added, h[0]]
    return h


def _parse_kan(meld):
    hai0 = (meld & 0xff00) >> 8
    kui = meld & 0x3
    if not kui:  # Ankan
        hai0 = (hai0 & ~3) +3
    t = (hai0 // 4) * 4
    h = [t, t, t]
    rem = hai0 % 4
    if rem == 0:
        h[0] += 1
        h[1] += 2
        h[2] += 3
    elif rem == 1:
        h[0] += 0
        h[1] += 2
        h[2] += 3
    elif rem == 2:
        h[0] += 0
        h[1] += 1
        h[2] += 3
    else:
        h[0] += 0
        h[1] += 1
        h[2] += 2
    if kui == 1:
        hai0, h[2] = h[2], hai0
    if kui == 2:
        hai0, h[0] = h[0], hai0
    return [hai0] + h if kui else h[:2]


def _parse_call(attrib):
    meld = int(attrib['m'])
    _LG.debug('  Meld: %s', bin(meld))
    if meld & (1 << 2):
        mentsu = _parse_shuntsu(meld)
        type_ = 'Chi'
    elif meld & (1 << 3):
        type_ = 'Pon'
        mentsu = _parse_koutsu(meld)
    elif meld & (1 << 4):
        type_ = 'ChanKan'
        mentsu = _parse_chankan(meld)
    elif meld & (1 << 5):
        type_ = 'Nuki'
        mentsu = [120]  # PE-nuki
    else:
        type_ = 'Kan'
        mentsu = _parse_kan(meld)

    tiles = u''.join([_tile2unicode(tile) for tile in mentsu])
    player = int(attrib['who'])
    from_ = meld & 0x3
    from_str = u'from player {}'.format((player + from_) % 4)
    if from_ == 0:
        from_str = u''
    _LG.info(u'Player %s: %s %s: %s', player, type_, from_str, tiles)


def _parse_reach(attrib):
    who, step = int(attrib['who']), int(attrib['step'])
    if step == 1:
        _LG.info(u'Player %s: Reach', who)
    elif step == 2:
        # Old logs do not have ten values.
        if 'ten' in attrib:
            ten = _parse_int_list(attrib['ten'])
            _LG.info(u'Player %s: Deposite. Scores: %s', who, ten)
    else:
        raise NotImplementedError('Unexpected condition. {}'.format(attrib))


def _nest_list(vals):
    return list(zip(vals[::2], vals[1::2]))


_YAKU_NAME = [
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


_LIMIT_NAME = [
    'No limit',
    'Mangan',
    'Haneman',
    'Baiman',
    'Sanbaiman',
    'Yakuman',
]


def _parse_agari(attrib):
    who = int(attrib['who'])
    from_ = int(attrib['fromWho'])
    hand = _parse_int_list(attrib['hai'])
    machi = _parse_int_list(attrib['machi'])
    dora = _parse_int_list(attrib['doraHai'])
    ura_dora = _parse_int_list(attrib.get('doraHaiUra', ''))
    yaku = _nest_list(_parse_int_list(attrib['yaku']))
    yakuman = _nest_list(_parse_int_list(attrib.get('yakuman', '')))
    ten = _parse_int_list(attrib['ten'])
    ba = _parse_int_list(attrib['ba'])
    scores = _nest_list(_parse_int_list(attrib['sc']))
    _LG.info('Player %s won.', who)
    if from_ == who:
        _LG.info('  Tsumo.')
    else:
        _LG.info('  Ron from player %s', from_)
    _LG.info('  Hand: %s', _parse_hand(hand))
    _LG.info('  Machi: %s', _parse_hand(machi))
    _LG.info('  Dora: %s', _parse_hand(dora))
    if ura_dora:
        _LG.info('  Ura Dora: %s', _parse_hand(ura_dora))
    _LG.info('  Yaku:')
    for yaku_, han in yaku:
        _LG.info('      %s (%s): %s [Han]', _YAKU_NAME[yaku_], yaku_, han)
    if yakuman:
        _LG.info('  Yakuman:')
        for yaku_, han in yakuman:
            _LG.info('      %s (%s): %s [Han]', _YAKU_NAME[yaku_], yaku_, han)
    _LG.info('  Fu: %s', ten[0])
    _LG.info('  Ten: %s', ten[1])
    if ten[2]:
        _LG.info('  Limit: %s', _LIMIT_NAME[ten[2]])
    _LG.info('  Ten-bou:')
    _LG.info('    Combo: %s', ba[0])
    _LG.info('    Riichi: %s', ba[1])
    _LG.info('  Scores:')
    for cur, def_ in scores:
        _LG.info('    %s: %s', cur, def_)

    if 'owari' in attrib:
        final_scores = _nest_list(_parse_float_list(attrib['owari']))
        _LG.info('  Final scores:')
        for score, uma in final_scores:
            _LG.info('    %s: %s', score, uma)


def _parse_dora(attrib):
    hai = _parse_int_list(attrib['hai'])
    _LG.info('New Dora Indicator: %s', _parse_hand(hai))


_RYUKYOKU_TYPE = {
    'nm': 'nagashi_mangan',
    'yao9': '9shu9hai',
    'kaze4': '4 Fu',
    'reach4': '4 Reach',
    'ron3': '3 Ron',
    'kan4': '4 Kan',
}


def _parse_ryuukyoku(attrib):
    _LG.info('Ryukyoku:')
    if 'type' in attrib:
        _LG.info('  Reason: %s', _RYUKYOKU_TYPE[attrib['type']])
    for i, key in enumerate(['hai0', 'hai1', 'hai2', 'hai3']):
        if key not in attrib:
            continue
        hand = _parse_int_list(attrib[key])
        _LG.info('Player %s: %s', i, _parse_hand(hand))
    scores = _nest_list(_parse_int_list(attrib['sc']))
    for cur, def_ in scores:
        _LG.info('    %s: %s', cur, def_)
    ba = _parse_int_list(attrib['ba'])
    _LG.info('  Ten-bou:')
    _LG.info('    Combo: %s', ba[0])
    _LG.info('    Riichi: %s', ba[1])

    if 'owari' in attrib:
        final_scores = _nest_list(_parse_float_list(attrib['owari']))
        _LG.info('  Final scores:')
        for score, uma in final_scores:
            _LG.info('    %s: %s', score, uma)


def _parse_bye(attrib):
    _LG.info('Player %s has left the game.', attrib['who'])


def _parse_node(tag, attrib):
    _LG.debug('%s: %s', tag, attrib)
    if tag == 'GO':
        _parse_lobby(attrib)
    elif tag == 'UN':
        _parse_player(attrib)
    elif tag == 'TAIKYOKU':
        _parse_game(attrib)
    elif tag == 'SHUFFLE':
        pass
    elif tag == 'INIT':
        _parse_initial(attrib)
    elif tag == 'DORA':
        _parse_dora(attrib)
    elif tag[0] in {'T', 'U', 'V', 'W'}:
        _parse_draw(tag)
    elif tag[0] in {'D', 'E', 'F', 'G'}:
        _parse_discard(tag)
    elif tag == 'N':
        _parse_call(attrib)
    elif tag == 'REACH':
        _parse_reach(attrib)
    elif tag == 'AGARI':
        _parse_agari(attrib)
    elif tag == 'RYUUKYOKU':
        _parse_ryuukyoku(attrib)
    elif tag == 'BYE':
        _parse_bye(attrib)
    else:
        raise NotImplementedError('{}: {}'.format(tag, attrib))


def parse_mjlog(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    for child in root:
        _parse_node(child.tag, child.attrib)
