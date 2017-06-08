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
        self.dora = [data['dora']]

    def to_repr(self, level=0):
        vals = []
        vals.append(u'Oya:   %s' % self.oya)
        vals.append(u'Dices: %s, %s' % (self.dices[0], self.dices[1]))
        vals.append(u'Combo: %s' % self.combo)
        vals.append(u'Reach: %s' % self.reach)
        vals.append(u'Dora:  %s' % convert_hand(self.dora))
        return _indent(vals, level=level)


def _validate_tile_range(val):
    if val < 0 or val > 135:
        raise ValueError('Invalid hand value was given')


class Tiles(_ReprMixin, object):
    def __init__(self, tiles, sort):
        for tile in tiles:
            _validate_tile_range(tile)
        self.tiles = tiles
        self.sort = sort
        if self.sort:
            self.tiles.sort()

    def add(self, tile):
        _validate_tile_range(tile)
        self.tiles.append(tile)
        if self.sort:
            self.tiles.sort()

    def remove(self, tile):
        self.tiles.remove(tile)

    def __len__(self):
        return len(self.tiles)

    def __contains__(self, item):
        return item in self.tiles

    def __iter__(self):
        return iter(self.tiles)

    def to_repr(self, level=0):
        str_exp = u''.join(convert_hand(self.tiles))
        return _indent([str_exp], level=level)


class Hand(_ReprMixin, object):
    def __init__(self, tiles):
        self.menzen = True
        self.hidden = Tiles(tiles, sort=True)
        self.exposed = []
        self.nuki = Tiles([], sort=True)
        self.reach = False

    def add(self, tile):
        self.hidden.add(tile)

    def remove(self, tile):
        self.hidden.remove(tile)

    def __contains__(self, tile):
        return (
            tile in self.hidden or
            any(tile in tiles for tiles in self.exposed)
        )

    def _expose_pon_or_chi(self, mentsu):
        n_errors = 0
        for tile in mentsu:
            try:
                self.hidden.remove(tile)
            except ValueError:
                n_errors += 1
        if not n_errors == 1:
            raise AssertionError('Two tiles of mentsu must be present in hand.')
        self.exposed.append(
            Tiles(mentsu, sort=True)
        )
        self.menzen = False

    def _expose_nuki(self, tile):
        self.hidden.remove(tile)
        self.nuki.add(tile)

    def _expose_ankan(self, mentsu):
        base = mentsu[0] - mentsu[0] % 4
        full_mentsu = [base + i for i in range(4)]
        for tile in full_mentsu:
            self.hidden.remove(tile)
        self.exposed.append(
            Tiles(full_mentsu, sort=True)
        )

    def expose(self, call_type, mentsu):
        if call_type in ['Pon', 'Chi']:
            self._expose_pon_or_chi(mentsu)
        elif call_type == 'Nuki':
            self._expose_nuki(mentsu[0])
        elif call_type == 'Ankan':
            self._expose_ankan(mentsu)
        else:
            raise NotImplementedError(call_type)

    def to_repr(self, level=0):
        vals = []
        if self.reach:
            vals.append(u'Menzen, Reach')
        elif self.menzen:
            vals.append(u'Menzen')
        vals.extend(self.hidden.to_repr(level=0))
        for tiles in self.exposed:
            vals.extend(tiles.to_repr(level=0))
        if len(self.nuki):
            vals.extend(self.nuki.to_repr(level=0))
        return _indent(vals, level=level)


class Discards(_ReprMixin, object):
    def __init__(self):
        self.tiles = Tiles([], sort=False)
        self.taken = []

    def to_repr(self, level=0):
        vals = []
        takens = [' ' if val is None else str(val) for val in self.taken]
        vals.append(u' '.join(self.tiles.to_repr()))
        vals.append(u'   '.join([ensure_unicode(val) for val in takens]))
        return _indent(vals, level=level)

    def add(self, tile):
        self.tiles.add(tile)
        self.taken.append(None)

    def mark_taken(self, player):
        self.taken[-1] = player

class Player(_ReprMixin, object):
    def __init__(self):
        self.score = 0
        self.hand = None
        self.discards = Discards()
        self.available = True

    def set_score(self, score):
        """Set score of the player

        Parameters
        ----------
        score : int
        """
        self.score = score

    def set_hand(self, tiles):
        """Set hand of the player

        Parameters
        ----------
        tiles : list of int
        """
        self.hand = Hand(tiles)

    def draw(self, tile):
        """Draw new tile

        Parameter
        ---------
        tile : int
        """
        self.hand.add(tile)

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
        self.discards.add(tile)

    def mark_taken(self, player):
        self.discards.mark_taken(player)

    def expose(self, call_type, mentsu):
        self.hand.expose(call_type, mentsu)

    def to_repr(self, level):
        ret = []
        if self.score:
            ret.append(u'Score: %s' % self.score)
        if self.hand:
            hand_repr = self.hand.to_repr()
            ret.append(u'Hand:     %s' % hand_repr[0])
            for exposed in hand_repr[1:]:
                ret.append(u'          %s' % exposed)
        if self.discards:
            disc_repr = self.discards.to_repr()
            ret.append(u'Discard:  %s' % disc_repr[0])
            ret.append(u'          %s' % disc_repr[1])
        return _indent(ret, level=level)


class Round(_ReprMixin, object):
    def __init__(self, index, config, mode):
        self.index = index
        self.mode = mode
        self.config = config

        n_players = 3 if self.mode.sanma else 4
        self.players = [Player() for _ in range(n_players)]

        self.last_discard = {}
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
        if self.last_discard:
            tile = convert_hand([self.last_discard['tile']])
            vals.append('  Last Discard:')
            vals.append('    Player: %s' % self.last_discard['player'])
            vals.append('    tile: %s' %  tile)
        if self.ryuukyoku_reason:
            vals.append('  Ryuukyoku: %s', self.ryuukyoku_reason)
        return _indent(vals, level=level)

    def get_top_players(self):
        players = sorted(self.players, key=lambda x: x.score, reverse=True)
        top_score = players[0].score
        return [player for player in players if player.score == top_score]

    def init_players(self, hands, scores):
        for player, hand, score in zip(self.players, hands, scores):
            player.set_hand(hand)
            player.set_score(score)

    def draw(self, player, tile):
        self.players[player].draw(tile)

    def discard(self, player, tile):
        self.players[player].discard(tile)
        self.last_discard = {'player': player, 'tile': tile}

    def call(self, caller, callee, call_type, mentsu):
        caller_, callee_ = self.players[caller], self.players[callee]
        if call_type in ['Chi', 'Pon']:
            callee_.mark_taken(caller)
            caller_.expose(call_type, mentsu)
        elif call_type == 'Nuki':
            caller_.expose(call_type, mentsu)
        elif call_type == 'Kan':
            if caller == callee:
                caller_.expose('Ankan', mentsu)
            else:
                raise NotImplementedError('MinKan')
        else:
            raise NotImplementedError(
                '%s: %s, %s, %s' % (call_type, caller, callee, convert_hand(mentsu)))

    def reach(self, player, step, score=None):
        player_ = self.players[player]
        if step == 1:
            player_.hand.reach = True
        elif step == 2:
            player_.score -= 1000
            self.config.reach += 1
            if score:
                raise NotImplementedError('Add score assertion here.')
        else:
            raise NotImplementedError('Unexpected step value: {}'.format(step))

    def agari(self, **data):
        for i, (current, diff) in enumerate(data['scores']):
            player = self.players[i]
            if not player.score == current:
                raise ValueError(
                    (
                        'Player score does not match to what is reported. '
                        'Check implementation. Current: %s, Reported: %s'
                    ) % (player.score, current)
                )
            player.score += diff
        ba = data['ba']
        if self.config.reach != ba['reach']:
            raise ValueError(
                (
                    '#Reach sticks on table does not match with what is reported.'
                    'Check implementation. Current: %s, Reported: %s'
                ) % (self.config.reach, ba['reach'])
            )
        self.config.reach = 0
        if self.config.combo != ba['combo']:
            raise ValueError(
                (
                    '#Combo sticks on table does not match with what is reported.'
                    'Check implementation. Current: %s, Reported: %s'
                ) % (self.config.combo, ba['combo'])
            )
        # skip ten(Fu, Point, limit), yaku, yakuman, dora, ura-dora
        _LG.info('Currently, no point conputation is carried out.')

        # Validate winning hand
        winner = self.players[data['winner']]
        for tile in winner.hand.hidden:
            if tile not in data['hand']:
                raise AssertionError(
                    'Winning hand does not contain the reported tile. '
                    'Check implementation.'
                )

        if 'loser' in data:
            if data['loser'] != self.last_discard['player']:
                raise AssertionError(
                    'Loser and the player who dicarded a tile '
                    'does not match.'
                )
            if data['machi'][0] != self.last_discard['tile']:
                raise AssertionError(
                    'Machi tile and the tile lastly discarded '
                    'does not match.'
                )

    def ryuukyoku(self, hands, scores, ba, reason=None, result=None):
        for hand in hands:
            for player in self.players:
                if player.hand.hidden.tiles == hand:
                    break
            else:
                raise ValueError(
                    (
                        'Player hand does not match with what is reported. '
                        'Check implementation. Current: %s, Reported: %s'
                    ) % (player.hand, hand)
                )
        for player, (score, diff) in zip(self.players, scores):
            if not player.score == score:
                raise ValueError(
                    (
                        'Player score does not match with what is reported. '
                        'Check implementation. Current: %s, Reported: %s'
                    ) % (player.score, score)
                )
            player.score += diff

        if not self.config.reach == ba['reach']:
            raise ValueError(
                (
                    '#Reach sticks on table does not match with what is reported.'
                    'Check implementation. Current: %s, Reported: %s'
                ) % (self.config.reach, ba['reach'])
            )
        if not self.config.combo == ba['combo']:
            raise ValueError(
                (
                    '#Combo sticks on table does not match with what is reported.'
                    'Check implementation. Current: %s, Reported: %s'
                ) % (self.config.combo, ba['combo'])
            )
        if reason:
            self.ryuukyoku_reason = reason

        if result:
            if self.config.reach:
                top_players = self.get_top_players()
                if len(top_players) != 1:
                    raise NotImplementedError()
                top_players[0].score += 1000 * self.config.reach
                self.config.reach = 0
            for player, score in zip(self.players, result['scores']):
                if not player.score == score:
                    raise ValueError(
                        (
                            'Player score does not match with what is reported. '
                            'Check implementation. Current: %s, Reported: %s'
                        ) % (player.score, score)
                    )

    def bye(self, index):
        self.players[index].available = False

    def resume(self, index, **_):
        self.players[index].available = True


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

        if self.past_rounds:
            cur_round = self.round
            prev_round = self.past_rounds[-1]
            for prev_p, cur_p in zip(prev_round.players, cur_round.players):
                if prev_p.score != cur_p.score:
                    raise AssertionError(
                        (
                            'The previous score does not match to new one. '
                            'Check implementation. Current: %s, Reported: %s'
                        ) % (prev_p.score, cur_p.score)
                    )

    def set_uma(self, uma):
        self.uma = uma

    def archive_round(self):
        self.past_rounds.append(self.round)

def _process_go(game, data):
    _LG.info('Configuring game.')
    game.set_table(data['table'])
    game.set_mode(data['mode'])


def _process_un(game, data):
    _LG.info('Initializing Players.')
    game.init_players(data)


def _process_init(game, data):
    _LG.info('Initializing round.')
    game.init_round(data)

def _process_draw(game, data):
    game.round.draw(**data)


def _process_discard(game, data):
    game.round.discard(**data)


def _process_call(game, data):
    game.round.call(**data)


def _process_reach(game, data):
    game.round.reach(**data)


def _process_agari(game, data):
    for key, value in data.items():
        if key in ['hand', 'machi', 'dora']:
            value = convert_hand(value)
        _LG.info('%s: %s', key, value)

    game.round.agari(**data)
    game.archive_round()
    if 'result' in data:
        game.set_uma(data['result']['uma'])


def _process_ryuukyoku(game, data):
    for key, value in data.items():
        if key in ['hand', 'machi', 'dora']:
            value = convert_hand(value)
        if key in ['hands']:
            value = [convert_hand(hand) for hand in value]
        _LG.info('%s: %s', key, value)

    game.round.ryuukyoku(**data)
    game.archive_round()
    if 'result' in data:
        game.set_uma(data['result']['uma'])


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


def analyze_mjlog(parsed_log_data):
    game = Game()
    try:
        _analyze_mjlog(game, parsed_log_data)
    except Exception as e:
        print(game.round)
        raise e
