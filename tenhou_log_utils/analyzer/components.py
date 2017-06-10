from __future__ import unicode_literals
from __future__ import print_function

import abc
import logging

from tenhou_log_utils.io import ensure_str, ensure_unicode
from tenhou_log_utils.viewer import convert_hand

_LG = logging.getLogger(__name__)
# pylint: disable=too-few-public-methods


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


class PlayerInfo(_ReprMixin, object):
    """Player information"""
    def __init__(self, data):
        self.name = data['name']
        self.dan = data['dan']
        self.rate = data['rate']

    def to_repr(self, level=0):
        ret = [u'%3s [Dan], %8.2f, %s' % (self.dan, self.rate, self.name)]
        return _indent(ret, level=level)


class Config(_ReprMixin, object):
    """Game configuration"""
    def __init__(self, config):
        self.red = config['red']
        self.kui = config['kui']
        self.soku = config['soku']
        self.sanma = config['sanma']
        self.ton_nan = config['ton-nan']

    def to_repr(self, level=0):
        vals = [
            (u'Red' if self.red else u'No Red'),
            (u'Kui' if self.kui else u'No Kui'),
            (u'Ton-Nan' if self.ton_nan else u'Ton-Pu'),
        ]
        if self.sanma:
            vals.append(u'Sanma')
        if self.soku:
            vals.append(u'Soku')
        return _indent(vals, level=level)


class State(_ReprMixin, object):
    """State of game common to the players"""
    def __init__(self, data):
        self.oya = data['oya']
        self.combo = data['combo']
        self.reach = data['reach']
        self.dices = data['dices']
        self.dora = [data['dora']]
        field = data['round'] // 4
        self.round = {
            'repeat': field // 4,  # #Kaeri-Ton
            'field': field % 4,  # Ton, Nan, Xia, Pei ...
            'match': data['round'] % 4,
        }

    def to_repr(self, level=0):
        rep = self.round['repeat']
        match = self.round['match'] + 1
        field = ['Ton', 'Nan', 'Xia', 'Pei'][self.round['field'] % 4]
        if self.round['repeat']:
            rounds = u'Round: %s %s %s Kyoku' % (rep, field, match)
        else:
            rounds = u'Round: %s %s Kyoku' % (field, match)

        vals = [rounds]
        vals.append(u'Oya:   %s' % self.oya)
        vals.append(u'Dices: %s, %s' % (self.dices[0], self.dices[1]))
        vals.append(u'Combo: %s' % self.combo)
        vals.append(u'Reach: %s' % self.reach)
        vals.append(u'Dora:  %s' % convert_hand(self.dora))
        return _indent(vals, level=level)


def _validate_tile_ranges(vals):
    for val in vals:
        if not 0 <= val <= 135:
            raise ValueError('Invalid tile value (%s) was given' % val)


class Tiles(_ReprMixin, object):
    """Represent a set of tiles"""
    def __init__(self, tiles, sort):
        _validate_tile_ranges(tiles)
        self.tiles = tiles
        self.sort = sort
        if self.sort:
            self.tiles.sort()

    def to_repr(self, level=0):
        repr_ = [u''.join(convert_hand(self.tiles))]
        return _indent(repr_, level=level)

    def add(self, tile):
        """Add a new tile"""
        _validate_tile_ranges([tile])
        self.tiles.append(tile)
        if self.sort:
            self.tiles.sort()

    def remove(self, *tiles):
        """Remove tiles"""
        for tile in tiles:
            try:
                self.tiles.remove(tile)
            except ValueError:
                raise ValueError(
                    'Cannot remove %s from %s' % (tile, self.tiles)
                )

    def __len__(self):
        return len(self.tiles)

    def __contains__(self, item):
        return item in self.tiles

    def __getitem__(self, index):
        return self.tiles[index]

    def __iter__(self):
        return iter(self.tiles)

    def __eq__(self, other):
        if isinstance(other, list):
            return sorted(self.tiles) == sorted(other)
        if isinstance(other, Tiles):
            return sorted(self.tiles) == sorted(other.tiles)
        return NotImplemented


class Hand(_ReprMixin, object):
    """Player hand"""
    def __init__(self, tiles):
        self.closed = Tiles(tiles, sort=True)
        self.exposed = []
        self.nuki = Tiles([], sort=True)

        self.menzen = True
        self.reach = False

    def to_repr(self, level=0):
        vals = []
        if self.reach:
            vals.append(u'Menzen, Reach')
        elif self.menzen:
            vals.append(u'Menzen')
        for tiles in [self.closed] + self.exposed:
            vals.extend(tiles.to_repr(level=0))
        if len(self.nuki):
            vals.extend(self.nuki.to_repr(level=0))
        return _indent(vals, level=level)

    def add(self, tile):
        """Add a new tile to closed hand."""
        self.closed.add(tile)

    def remove(self, tile):
        """Remove a tile from closed hand."""
        self.closed.remove(tile)

    def expose(self, call_type, mentsu):
        """Move tiles from closed to exposed.

        Parameters
        ----------
        call_type : str
            Either 'Pon', 'Chi', 'MinKan', 'Ankan' or 'Nuki'

        mentsu : list of int
            #elements must be
            - 1 for 'Nuki'
            - 2 for 'AnKan'
            - 3 for 'Pon' and 'Chi'
            - 4 for 'MinKan'
        """
        if call_type in ['Pon', 'Chi', 'MinKan']:
            self._expose_pon_kan_chi(mentsu)
        elif call_type == 'Nuki':
            self._expose_nuki(mentsu)
        elif call_type == 'AnKan':
            self._expose_ankan(mentsu)
        else:
            raise NotImplementedError('%s: %s' % (call_type, mentsu))

    def _expose_nuki(self, mentsu):
        if len(mentsu) != 1:
            raise AssertionError('Unexpected mentsu for Nuki.')
        self.closed.remove(mentsu[0])
        self.nuki.add(mentsu[0])

    def _expose_ankan(self, mentsu):
        """Move tiles which compose An-Kan from covered to exposed

        Parameters
        ----------
        mentsu : list of two ints
            2 tiles uncovered when calling An-Kan.
        """
        base = mentsu[0] - mentsu[0] % 4
        full_mentsu = [base + i for i in range(4)]
        self.closed.remove(*full_mentsu)
        self.exposed.append(Tiles(full_mentsu, sort=True))

    def _expose_pon_kan_chi(self, mentsu):
        if sum([tile not in self.closed for tile in mentsu]) != 1:
            raise AssertionError(
                'Exactly one tile of mentsu must be missing from hand.')
        for tile in mentsu:
            if tile in self.closed:
                self.closed.remove(tile)
        self.exposed.append(Tiles(mentsu, sort=True))
        self.menzen = False

    def find_kan(self, base):
        """Find the corresponding Kan mentsu from exposed mentsu"""
        for mentsu in self.exposed:
            for tile in mentsu:
                if base == 4 * (tile // 4):
                    return mentsu
        raise ValueError('No corresponding Kan mentsu was found.')

    def __contains__(self, tile):
        return any(tile in tiles for tiles in [self.closed] + self.exposed)


class Discards(_ReprMixin, object):
    """Discarded tiles"""
    def __init__(self):
        self.tiles = Tiles([], sort=False)
        self.taken = []

    def to_repr(self, level=0):
        vals = [u' '.join(self.tiles.to_repr())]
        takens = [' ' if val is None else str(val) for val in self.taken]
        vals.append(u'   '.join([ensure_unicode(val) for val in takens]))
        return _indent(vals, level=level)

    def add(self, tile):
        """Add a tile to discard pile"""
        self.tiles.add(tile)
        self.taken.append(None)

    def mark_taken(self, player):
        """Mark the last discarded tile as taken"""
        self.taken[-1] = player


class Player(_ReprMixin, object):
    """Player hands and discards"""
    def __init__(self):
        self.score = 0
        self.hand = None
        self.discards = Discards()
        self.available = True

    def to_repr(self, level=0):
        ret = [u'Score: %s' % self.score]
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
        """Mark the last discarded pile as taken"""
        self.discards.mark_taken(player)

    def expose(self, call_type, mentsu):
        """Expose some tiles according to the call made"""
        self.hand.expose(call_type, mentsu)


def _validate_discarded(mentsu, callee, last_discarded):
    if last_discarded['player'] != callee:
        raise AssertionError(
            'Player who discarded last (%s) does not match callee (%s)'
            % (last_discarded['player'], callee)
        )
    
    if last_discarded['tile'] not in mentsu:
        raise AssertionError(
            'Last discarded tile (%s) is not included in mentsu; %s'
            % (last_discarded, mentsu)
        )

def _validate_score(players, scores):
    for player, (score, _) in zip(players, scores):
        if not player.score == score:
            raise AssertionError(
                (
                    'Player score does not match with what is reported. '
                    'Check implementation. Current: %s, Reported: %s'
                ) % (player.score, score)
            )


def _validate_sticks(state, expected):
    if state.reach != expected['reach']:
        raise AssertionError(
            (
                '#Reach sticks on table does not match with what is reported.'
                'Check implementation. Current: %s, Reported: %s'
            ) % (state.reach, expected['reach'])
        )
    if state.combo != expected['combo']:
        raise AssertionError(
            (
                '#Combo sticks on table does not match with what is reported.'
                'Check implementation. Current: %s, Reported: %s'
            ) % (state.combo, expected['combo'])
        )

def _validate_furikomi(player, tile, last_discard):
    if player != last_discard['player']:
        raise AssertionError(
            'Loser and the player who dicarded a tile '
            'does not match.'
        )
    if tile != last_discard['tile']:
        raise AssertionError(
            'Machi tile and the tile lastly discarded '
            'does not match.'
        )


def _validate_ryuukyoku_hands(players, hands):
    for player, hand in zip(players, hands):
        if hand is None:
            continue
        if player.hand.closed != hand:
            raise ValueError(
                (
                    'Player hand does not match with what is reported. '
                    'Check implementation. Current: %s, Reported: %s'
                ) % (player.hand, hand)
            )


class Round(_ReprMixin, object):
    def __init__(self, index, state, mode):
        self.index = index
        self.mode = mode
        self.state = state

        self.players = []
        self.last_discard = {}
        self.ryuukyoku_reason = None

    def to_repr(self, level=0):
        vals = [u'Round: %s' % self.index]
        vals.append(u'  Mode:')
        vals.extend(self.mode.to_repr(level=2))
        vals.append(u'  State:')
        vals.extend(self.state.to_repr(level=2))
        if self.last_discard:
            tile = convert_hand([self.last_discard['tile']])
            vals.append('  Last Discard:')
            vals.append('    Player: %s' % self.last_discard['player'])
            vals.append('    tile: %s' %  tile)
        if self.players:
            vals.append(u'  Players:')
            for player in self.players:
                vals.extend(player.to_repr(level=2))
        if self.ryuukyoku_reason:
            vals.append('  Ryuukyoku: %s', self.ryuukyoku_reason)
        return _indent(vals, level=level)

    def get_top_players(self):
        players = sorted(self.players, key=lambda x: x.score, reverse=True)
        top_score = players[0].score
        return [player for player in players if player.score == top_score]

    def init_players(self, hands, scores):
        n_players = 3 if self.mode.sanma else 4
        self.players = [Player() for _ in range(n_players)]
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
            _validate_discarded(mentsu, callee, self.last_discard)
            callee_.mark_taken(caller)
            caller_.expose(call_type, mentsu)
        elif call_type == 'Nuki':
            caller_.expose(call_type, mentsu)
        elif call_type == 'Kan':
            if caller == callee:
                caller_.expose('AnKan', mentsu)
            else:
                _validate_discarded(mentsu, callee, self.last_discard)
                caller_.expose('MinKan', mentsu)
        elif call_type == 'KaKan':
            base = 4 * (mentsu[0] // 4)
            mentsu_ = caller_.hand.find_kan(base)
            for tile in mentsu:
                if tile not in mentsu_:
                    mentsu_.add(tile)
                    caller_.hand.closed.remove(tile)
        else:
            raise NotImplementedError(
                '%s: %s, %s, %s' % (call_type, caller, callee, convert_hand(mentsu)))

    def reach(self, player, step, scores=None):
        player_ = self.players[player]
        if step == 1:
            player_.hand.reach = True
        elif step == 2:
            player_.score -= 1000
            self.state.reach += 1
            if scores:
                for player, score in zip(self.players, scores):
                    if player.score != score:
                        raise AssertionError(
                            'Player score does not match to what is reported. '
                            'Check implementation. Current: %s, Reported: %s'
                        ) % (player.score, score)
        else:
            raise NotImplementedError('Unexpected step value: {}'.format(step))

    def agari(self, scores, **data):
        _validate_score(self.players, scores)
        _validate_sticks(self.state, data['ba'])
        if 'loser' in data:
            _validate_furikomi(data['loser'], data['machi'][0], self.last_discard)

        for player, (_, gain) in zip(self.players, scores):
            player.score += gain

        self.state.reach = 0
        # TODO: Combostick?

        # skip ten(Fu, Point, limit), yaku, yakuman, dora, ura-dora
        _LG.info('Currently, no point conputation is carried out.')

        # Validate winning hand
        winner = self.players[data['winner']]
        for tile in winner.hand.closed:
            if tile not in data['hand']:
                raise AssertionError(
                    'Winning hand is not contained the reported tile. '
                    'Check implementation.'
                )
        if 'result' in data:
            _validate_score(self.players, data['result'])

    def ryuukyoku(self, hands, scores, ba, reason=None, result=None):
        _validate_score(self.players, scores)
        _validate_sticks(self.state, ba)
        _validate_ryuukyoku_hands(self.players, hands)

        for player, (_, diff) in zip(self.players, scores):
            player.score += diff

        if reason:
            self.ryuukyoku_reason = reason

        if result:
            if self.state.reach:
                top_players = self.get_top_players()
                if len(top_players) != 1:
                    raise NotImplementedError()
                top_players[0].score += 1000 * self.state.reach
                self.state.reach = 0
            _validate_score(self.players, result)

    def bye(self, index):
        self.players[index].available = False

    def resume(self, index, **_):
        self.players[index].available = True


class Game(_ReprMixin, object):
    def __init__(self):
        self.table = None
        self.config = None
        self.round = None
        self.players = []
        self.past_rounds = []
        self.uma = None

        self.n_draw = 0
        self.n_discard = 0
        self.n_kan = 0
        self.n_pon = 0
        self.n_chi = 0

    def to_repr(self, level=0):
        ret = self.round.to_repr(level=0)
        return _indent(ret, level=level)

    def set_table(self, table):
        self.table = table

    def set_config(self, config):
        self.config = Config(config)

    def init_players(self, data):
        self.players = [PlayerInfo(datum) for datum in data]

    def init_round(self, data):
        state, hands, scores = State(data), data['hands'], data['scores']

        index = len(self.past_rounds)
        self.round = Round(index, state, self.config)
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
