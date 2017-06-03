from __future__ import division

import logging

_LG = logging.getLogger(__name__)


def _unquote(quoted):
    try:
        from urllib.parse import unquote
        return unquote(quoted)
    except ImportError:
        from urllib2 import unquote
        return unquote(quoted).decode('utf-8')


def _parse_str_list(val, type_):
    return [type_(val) for val in val.split(',')] if val else []


###############################################################################
def _parse_shuffle(attrib):
    return {
        'seed': attrib['seed'],
        'ref': attrib['ref'],
    }


###############################################################################
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


def _parse_go(attrib):
    type_ = _parse_lobby_type(int(attrib['type']))
    number_ = int(attrib.get('lobby', '-1'))
    return {'type': type_, 'num': number_}


###############################################################################
def _parse_un(attrib):
    if len(attrib) == 1:  # Disconnected player has returned
        index = int(list(attrib.keys())[0][1])
        name = _unquote(list(attrib.values())[0])
        return [(index, name, None, None, None)]


    indices, names = [], []
    for key in ['n0', 'n1', 'n2', 'n3']:
        if key in attrib:
            indices.append(int(key[1]))
            names.append(_unquote(attrib[key]))
    dans = attrib['dan'].split(',') if 'dan' in attrib else [None] * 4
    rates = attrib['rate'].split(',')
    sexes = attrib['sx'].split(',')

    result = []
    for i, name, dan, rate, sex in zip(indices, names, dans, rates, sexes):
        result.append((i, name, dan, rate, sex))
    return result


################################################################################
def _parse_taikyoku(attrib):
    return {'oya': attrib['oya']}


###############################################################################
def _parse_init(attrib):
    seed = _parse_str_list(attrib['seed'], type_=int)
    scores = _parse_str_list(attrib['ten'], type_=int)
    hands = [
        _parse_str_list(attrib[key], type_=int)
        for key in ['hai0', 'hai1', 'hai2', 'hai3'] if key in attrib
    ]
    return {
        'oya': attrib['oya'],
        'scores': scores,
        'hands': hands,
        'round': seed[0],
        'combo': seed[1],
        'reach': seed[2],
        'dice1': seed[3],
        'dice2': seed[4],
        'dora_indicator': seed[5],
    }


###############################################################################
def _parse_draw(tag):
    player = ord(tag[0]) - ord('T')
    tile = int(tag[1:])
    return {'player': player, 'tile': tile}


###############################################################################
def _parse_discard(tag):
    player = ord(tag[0]) - ord('D')
    tile = int(tag[1:])
    return {'player': player, 'tile': tile}


###############################################################################
def _parse_shuntsu(meld):
    # Adopted from http://tenhou.net/img/tehai.js
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
    # Adopted from http://tenhou.net/img/tehai.js
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
    # Adopted from http://tenhou.net/img/tehai.js
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
    # Adopted from http://tenhou.net/img/tehai.js
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
    player = int(attrib['who'])
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
        mentsu = meld >> 8
        # TODO: Check if this is correct.
    else:
        type_ = 'Kan'
        mentsu = _parse_kan(meld)
    from_ = (player + meld & 0x3) % 4  # Relative -> Absolute
    return {'player': player, 'from': from_, 'type': type_, 'mentsu': mentsu}


###############################################################################
def _parse_reach(attrib):
    who, step = int(attrib['who']), int(attrib['step'])
    if step > 2:
        raise NotImplementedError('Unexpected step value: {}'.format(attrib))

    result = {'player': who, 'step': step}
    # Old logs do not have ten values.
    if 'ten' in attrib:
        result['ten'] = _parse_str_list(attrib['ten'], type_=int)
    return result


################################################################################
def _nest_list(vals):
    if len(vals) % 2:
        raise RuntimeError('List with odd number of value was given.')
    return list(zip(vals[::2], vals[1::2]))


def _parse_agari(attrib):
    result = {
        'player': int(attrib['who']),
        'from': int(attrib['fromWho']),
        'hand': _parse_str_list(attrib['hai'], type_=int),
        'machi': _parse_str_list(attrib['machi'], type_=int),
        'dora': _parse_str_list(attrib['doraHai'], type_=int),
        'ura_dora': _parse_str_list(
            attrib.get('doraHaiUra', ''), type_=int),
        'yaku': _nest_list(_parse_str_list(attrib.get('yaku'), type_=int)),
        'yakuman': _parse_str_list(attrib.get('yakuman', ''), type_=int),
        'ten': _parse_str_list(attrib['ten'], type_=int),
        'ba': _parse_str_list(attrib['ba'], type_=int),
        'scores': _nest_list(_parse_str_list(attrib['sc'], type_=int)),
    }

    if 'owari' in attrib:
        result['final_scores'] = _nest_list(
            _parse_str_list(attrib['owari'], type_=float))
    return result


################################################################################
def _parse_dora(attrib):
    return {'hai': int(attrib['hai'])}


###############################################################################
def _parse_ryuukyoku(attrib):
    result = {
        'type': attrib.get('type', 'out'),
        'hands': [
            _parse_str_list(attrib[key], type_=int)
            for key in ['hai0', 'hai1', 'hai2', 'hai3'] if key in attrib
        ],
        'scores': _nest_list(_parse_str_list(attrib['sc'], type_=int)),
        'ba': _parse_str_list(attrib['ba'], type_=int),
    }
    if 'owari' in attrib:
        result['final_scores'] = _nest_list(
            _parse_str_list(attrib['owari'], type_=int))
    return result


###############################################################################
def _parse_bye(attrib):
    return {'player': int(attrib['who'])}


###############################################################################
def parse_node(tag, attrib):
    _LG.debug('%s: %s', tag, attrib)
    if tag == 'GO':
        result = _parse_go(attrib)
    elif tag == 'UN':
        result = _parse_un(attrib)
    elif tag == 'TAIKYOKU':
        result = _parse_taikyoku(attrib)
    elif tag == 'SHUFFLE':
        result = _parse_shuffle(attrib)
    elif tag == 'INIT':
        result = _parse_init(attrib)
    elif tag == 'DORA':
        result = _parse_dora(attrib)
    elif tag[0] in {'T', 'U', 'V', 'W'}:
        result = _parse_draw(tag)
        tag = 'DRAW'
    elif tag[0] in {'D', 'E', 'F', 'G'}:
        result = _parse_discard(tag)
        tag = 'DISCARD'
    elif tag == 'N':
        result = _parse_call(attrib)
        tag = 'CALL'
    elif tag == 'REACH':
        result = _parse_reach(attrib)
    elif tag == 'AGARI':
        result = _parse_agari(attrib)
    elif tag == 'RYUUKYOKU':
        result = _parse_ryuukyoku(attrib)
    elif tag == 'BYE':
        result = _parse_bye(attrib)
    else:
        raise NotImplementedError('{}: {}'.format(tag, attrib))
    _LG.debug('%s: %s', tag, result)
    return {'tag': tag, 'result': result}

###############################################################################
def parse_mjlog(root_node):
    data = []
    for node in root_node:
        data.append(parse_node(node.tag, node.attrib))
    return data
