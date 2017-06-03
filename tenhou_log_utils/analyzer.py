# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import abc
import logging

from tenhou_log_utils.viewer import convert_hand
from tenhou_log_utils.io import ensure_str, ensure_unicode

_LG = logging.getLogger(__name__)


def _ensure_unicodes(list_object):
    return [ensure_unicode(string) for string in list_object]


def _indent(strings, level=0):
    return [u'%s%s' % (u'  ' * level, string) for string in strings]


class _ReprMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_repr(self, level=0):
        """Generate list of string representations"""
        raise NotImplementedError()

    def __repr__(self):
        return ensure_str(u'\n'.join(_ensure_unicodes(self.to_repr())))


class PlayerMeta(_ReprMixin, object):
    """Contain player meta info"""
    def __init__(self, data):
        self.index = data['index']
        self.name = data['name']
        self.dan = data['dan']
        self.rate = data['rate']
        self.sex = data['sex']

    def to_repr(self, level=0):
        ret = []
        ret.append(
            u'%1d: %3s [Dan], %8.2f, %3s, %s' % (
                self.index, self.dan, self.rate, self.sex, self.name
            ),
        )
        return _indent(ret, level=level)


class Mode(_ReprMixin, object):
    def __init__(self, mode):
        self.red = mode['red']
        self.kui = mode['kui']
        self.ton_nan = mode['ton-nan']
        self.sanma = mode['sanma']
        self.soku = mode['soku']

    def to_repr(self, level=0):
        vals = []
        vals.append(u'Red' if self.red else u'No Red')
        vals.append(u'Kui' if self.kui else u'No Kui')
        vals.append(u'Ton-Nan' if self.ton_nan else u'Ton-Pu')
        if self.sanma:
            vals.append(u'Sanma')
        if self.soku:
            vals.append(u'Soku')
        return _indent(vals, level=level)


class Config(_ReprMixin, object):
    def __init__(self, data):
        self.oya = data['oya']
        self.combo = data['combo']
        self.reach = data['reach']
        self.dices = data['dices']
        self.dora_indicator = data['dora_indicator']

    def to_repr(self, level=0):
        vals = []
        vals.append(u'Oya:   %s' % self.oya)
        vals.append(u'Dices: %s, %s' % (self.dices[0], self.dices[1]))
        vals.append(u'Combo: %s' % self.combo)
        vals.append(u'Reach: %s' % self.reach)
        vals.append(u'Dora:  %s' % self.dora_indicator)
        return _indent(vals, level=level)


class Player(object):
    def __init__(self):
        self.score = None
        self.hand = None
        self.discards = []

    def set_score(self, score):
        """Set score of the player

        Parameters
        ----------
        score : int
        """
        self.score = score

    def set_hand(self, hand):
        """Set hand of the player

        Parameters
        ----------
        hand : list of int
        """
        self.hand = hand

    def draw(self, tile):
        """Draw new tile

        Parameter
        ---------
        tile : int
        """
        self.hand.append(tile)

    def discard(self, tile):
        """Discard a tile

        Parameter
        ---------
        tile : int

        Raises
        ------
        ValueError
            If the given tile does not exist, which should never happen.
        """
        self.hand.remove(tile)
        self.discards.append(tile)

    def to_repr(self, level):
        ret = []
        if self.score:
            ret.append(u'Score: %s' % self.score)
        if self.hand:
            ret.append(u'Hand:     %s' % convert_hand(self.hand, True))
        if self.discards:
            ret.append(u'Discard:  %s' % convert_hand(self.discards))
        return _indent(ret, level=level)


class Round(_ReprMixin, object):
    def __init__(self, index, config, mode):
        self.index = index
        self.mode = mode
        self.config = config

        n_players = 3 if self.mode.sanma else 4
        self.players = [Player() for _ in range(n_players)]

        self.ryuukyoku_reason = None

    def to_repr(self, level=0):
        vals = []
        vals.append(u'Round: %s' % self.index)
        vals.append(u'  Mode:')
        vals.extend(self.mode.to_repr(level=2))
        vals.append(u'  Config:')
        vals.extend(self.config.to_repr(level=2))
        vals.append(u'  Players:')
        for player in self.players:
            vals.extend(player.to_repr(level=2))
        if self.ryuukyoku_reason:
            vals.append('  Ryuukyoku: %s', self.ryuukyoku_reason)
        return _indent(vals, level=level)

    def init_players(self, hands, scores):
        for player, hand, score in zip(self.players, hands, scores):
            player.set_hand(hand)
            player.set_score(score)

    def draw(self, player, tile):
        self.players[player].draw(tile)

    def discard(self, player, tile):
        self.players[player].discard(tile)

    def ryuukyoku(self, hands, scores, ba, reason=None, result=None):
        for hand in hands:
            for i, player in enumerate(self.players):
                if sorted(player.hand) == hand:
                    break
            else:
                raise ValueError(
                    (
                        'Player hand does not match to what is reported. '
                        'Check implementation. Current: %s, Reported: %s'
                    ) % (player.hand, hand)
                )
        for player, (score, diff) in zip(self.players, scores):
            if not player.score == score:
                raise ValueError(
                    (
                        'Player score does not match to what is reported. '
                        'Check implementation. Current: %s, Reported: %s'
                    ) % (player.score, score)
                )
            player.score += diff

        if not self.config.reach == ba['reach']:
            raise ValueError(
                (
                    '#Reach sticks on table does not match to what is reported.'
                    'Check implementation. Current: %s, Reported: %s'
                ) % (self.config.reach, ba['reach'])
            )
        if not self.config.combo == ba['combo']:
            raise ValueError(
                (
                    '#Combo sticks on table does not match to what is reported.'
                    'Check implementation. Current: %s, Reported: %s'
                ) % (self.config.combo, ba['combo'])
            )
        if reason:
            self.ryuukyoku_reason = reason

        if result:
            for player, score in zip(self.players, result['scores']):
                if not player.score == score:
                    raise ValueError(
                        (
                            'Player score does not match to what is reported. '
                            'Check implementation. Current: %s, Reported: %s'
                        ) % (player.score, score)
                    )


class Game(object):
    def __init__(self):
        self.table = None
        self.mode = None
        self.round = None
        self.players = []
        self.past_rounds = []
        self.uma = None

        self.n_draw = 0
        self.n_discard = 0
        self.n_kan = 0
        self.n_pon = 0
        self.n_chi = 0

    def set_table(self, table):
        self.table = table

    def set_mode(self, mode):
        self.mode = Mode(mode)

    def init_players(self, data):
        self.players = [PlayerMeta(datum) for datum in data]

    def init_round(self, data):
        n_round, config = data['round'], Config(data)
        hands, scores = data['hands'], data['scores']

        self.round = Round(n_round, config, self.mode)
        self.round.init_players(hands, scores)

    def set_uma(self, uma):
        self.uma = uma

def _process_go(game, data):
    _LG.info('Configuring game.')
    game.set_table(data['table'])
    game.set_mode(data['mode'])


def _process_un(game, data):
    if len(data) == 1:
        raise NotImplementedError()
    else:
        _LG.info('Initializing Players.')
        game.init_players(data)


def _process_init(game, data):
    _LG.info('Initializing round.')
    game.init_round(data)

def _process_draw(game, data):
    game.round.draw(**data)


def _process_discard(game, data):
    game.round.discard(**data)


def _process_ryuukyoku(game, data):
    game.round.ryuukyoku(**data)
    if 'result' in data:
        game.set_uma(data['result']['uma'])


def analyze_mjlog(parsed_log_data):
    data_ = []
    game = Game()
    for result in parsed_log_data:
        tag, data = result['tag'], result['data']
        _LG.debug('%s: %s', tag, data)
        if tag == 'GO':
            _process_go(game, data)
        elif tag == 'TAIKYOKU':
            pass
        elif tag == 'UN':
            _process_un(game, data)
        elif tag == 'INIT':
            _process_init(game, data)
        elif tag == 'DRAW':
            _process_draw(game, data)
        elif tag == 'DISCARD':
            _process_discard(game, data)
        elif tag == 'RYUUKYOKU':
            _process_ryuukyoku(game, data)
        else:
            _LG.error('\n%s', game.round)
            if 'mentsu' in data:
                _LG.error(convert_hand(data['mentsu']))
            raise NotImplementedError('%s: %s' % (tag, data))

