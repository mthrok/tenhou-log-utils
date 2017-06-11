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
            raise ValueError(u'Invalid tile value (%s) was given' % val)


class Tiles(_ReprMixin, object):
    """Represent a set of tiles"""
    def __init__(self, tiles, sort, type=None):
        _validate_tile_ranges(tiles)
        self.tiles = tiles
        self.sort = sort
        self.type = type
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
                    'Tile %s does not exist in %s' % (tile, self.tiles)
                )

    def __len__(self):
        return len(self.tiles)

    def __contains__(self, item):
        return item in self.tiles

    def __getitem__(self, index):
        return self.tiles[index]

    def __iter__(self):
        return iter(self.tiles)

    def __add__(self, items):
        if isinstance(items, list):
            return Tiles(self.tiles + items, self.sort, self.type)
        if isinstance(items, int):
            return Tiles(self.tiles + [items], self.sort, self.type)
        raise NotImplementedError('Unexpected type %s' % type(items))

    def __eq__(self, other):
        if isinstance(other, list):
            return sorted(self.tiles) == sorted(other)
        if isinstance(other, Tiles):
            return sorted(self.tiles) == sorted(other.tiles)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, list):
            return sorted(self.tiles) != sorted(other)
        if isinstance(other, Tiles):
            return sorted(self.tiles) != sorted(other.tiles)
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
            self._expose_pon_kan_chi(mentsu, type=call_type)
        elif call_type == 'Nuki':
            self._expose_nuki(mentsu)
        elif call_type == 'AnKan':
            self._expose_ankan(mentsu, type=call_type)
        else:
            raise NotImplementedError(u'%s: %s' % (call_type, mentsu))

    def _expose_nuki(self, mentsu):
        if len(mentsu) != 1:
            raise AssertionError(u'Unexpected mentsu for Nuki.')
        self.closed.remove(mentsu[0])
        self.nuki.add(mentsu[0])

    def _expose_ankan(self, mentsu, type):
        """Move tiles which compose An-Kan from covered to exposed

        Parameters
        ----------
        mentsu : list of two ints
            2 tiles uncovered when calling An-Kan.
        """
        base = mentsu[0] - mentsu[0] % 4
        full_mentsu = [base + i for i in range(4)]
        self.closed.remove(*full_mentsu)
        self.exposed.append(Tiles(full_mentsu, sort=True, type=type))

    def _expose_pon_kan_chi(self, mentsu, type):
        if sum([tile not in self.closed for tile in mentsu]) != 1:
            raise AssertionError(
                'Exactly one tile of mentsu must be missing from hand.')
        for tile in mentsu:
            if tile in self.closed:
                self.closed.remove(tile)
        self.exposed.append(Tiles(mentsu, sort=True, type=type))
        self.menzen = False

    def find_pon(self, base):
        """Find the corresponding Pon mentsu from exposed mentsu"""
        for mentsu in self.exposed:
            if not mentsu.type == 'Pon':
                continue
            if base == 4 * (mentsu[0] // 4):
                return mentsu
        raise ValueError(u'No corresponding Pon mentsu was found.')

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
    def __init__(self, index, hand, score):
        self.index = index
        self.hand = hand
        self.score = score

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


def _validate_last_draw(player, last_draw):
    if player != last_draw:
        raise AssertionError(
            u'Player who declared reach (%s) does not match '
            'to the on who drew a tile last (%s).' % (player, last_draw)
        )


def _validate_discarded(mentsu, callee, last_discarded):
    if last_discarded['player'] != callee:
        raise AssertionError(
            u'Player who discarded last (%s) does not match callee (%s)'
            % (last_discarded['player'], callee)
        )

    if last_discarded['tile'] not in mentsu:
        raise AssertionError(
            u'Last discarded tile (%s) is not included in mentsu; %s'
            % (last_discarded, mentsu)
        )

def _validate_score(players, scores):
    for player, score in zip(players, scores):
        if not player.score == score:
            raise AssertionError(
                (
                    u'Player score does not match with what is reported. '
                    'Check implementation. Current: %s, Reported: %s'
                ) % (player.score, score)
            )


def _validate_sticks(state, expected):
    if state.reach != expected['reach']:
        raise AssertionError(
            (
                u'#Reach sticks on table does not match with what is reported.'
                'Check implementation. Current: %s, Reported: %s'
            ) % (state.reach, expected['reach'])
        )
    if state.combo != expected['combo']:
        raise AssertionError(
            (
                u'#Combo sticks on table does not match with what is reported.'
                'Check implementation. Current: %s, Reported: %s'
            ) % (state.combo, expected['combo'])
        )

def _validate_furikomi(player, tile, last_discard):
    if player != last_discard['player']:
        raise AssertionError(
            u'Loser and the player who dicarded a tile '
            'does not match.'
        )
    if tile != last_discard['tile']:
        raise AssertionError(
            u'Machi tile and the tile lastly discarded '
            'does not match.'
        )


def _validate_winning_hand(winner_hand, data):
    hand = winner_hand.closed + data['machi'] if 'loser' in data else winner_hand.closed
    if hand != data['hand']:
        raise AssertionError(
            'Winning hand is not contained the reported tile. '
            'Check implementation.'
        )


def _validate_ryuukyoku_hands(players, hands):
    for player, hand in zip(players, hands):
        if hand is None:
            continue
        if player.hand.closed != hand:
            expected = convert_hand(hand)
            found = convert_hand(player.hand.closed.tiles)
            message = (
                u'Player hand does not match with what is reported. '
                u'Check implementation. Expected: %s, Found: %s'
            ) % (expected, found)
            raise ValueError(ensure_str(message))


class Round(_ReprMixin, object):
    def __init__(self, index, state, mode):
        self.index = index
        self.mode = mode
        self.state = state

        self.players = []
        self.last_discard = {}
        self.last_draw = {}
        self.ryuukyoku_reason = None

    def to_repr(self, level=0):
        vals = [u'Round: %s' % self.index]
        vals.append(u'  Mode:')
        vals.extend(self.mode.to_repr(level=2))
        vals.append(u'  State:')
        vals.extend(self.state.to_repr(level=2))
        if self.last_draw:
            tile = convert_hand([self.last_draw['tile']])
            vals.append(u'  Last Draw:')
            vals.append(u'    Player: %s' % self.last_draw['player'])
            vals.append(u'    tile: %s' %  tile)
        if self.last_discard:
            tile = convert_hand([self.last_discard['tile']])
            vals.append(u'  Last Discard:')
            vals.append(u'    Player: %s' % self.last_discard['player'])
            vals.append(u'    tile: %s' %  tile)
        if self.players:
            vals.append(u'  Players:')
            for player in self.players:
                vals.extend(player.to_repr(level=2))
        if self.ryuukyoku_reason:
            vals.append(u'  Ryuukyoku: %s' % self.ryuukyoku_reason)
        return _indent(vals, level=level)

    def init_players(self, tiles, scores):
        """Initialize players

        Parameters
        ----------
        tiles : list of ints
        scores : list of ints
        """
        for index, (tiles_, score) in enumerate(zip(tiles, scores)):
            if self.mode.sanma and index == 3:
                break
            hand = Hand(tiles_)
            self.players.append(Player(index, hand, score))

    def _get_top_players(self):
        """Get the list of players with the highest scores"""
        players = sorted(self.players, key=lambda x: x.score, reverse=True)
        top_score = players[0].score
        return [player for player in players if player.score == top_score]

    def draw(self, player, tile):
        """Add new tile to player

        Parameters
        ----------
        player : int
        tile : int
        """
        self.players[player].draw(tile)
        self.last_draw = {'player': player, 'tile': tile}

    def discard(self, player, tile):
        """Remove a tile from player

        Parameters
        ----------
        player : int
        tile : int
        """
        self.players[player].discard(tile)
        self.last_discard = {'player': player, 'tile': tile}

    def call(self, caller, callee, call_type, mentsu):
        """Process call

        Parameters
        ----------
        caller : int
        callee : int
        call_type : str
            Either 'Chi', 'Pon', 'Nuki', 'AnKan', 'MinKan' or 'KaKan'
        mentsu : list of ints
        """
        caller_, callee_ = self.players[caller], self.players[callee]
        if call_type in ['Chi', 'Pon']:
            _validate_discarded(mentsu, callee, self.last_discard)
            callee_.mark_taken(caller)
            caller_.expose(call_type, mentsu)
        elif call_type == 'Nuki':
            caller_.expose(call_type, mentsu)
        elif call_type == 'AnKan':
            caller_.expose(u'AnKan', mentsu)
        elif call_type == 'MinKan':
            _validate_discarded(mentsu, callee, self.last_discard)
            caller_.expose(u'MinKan', mentsu)
        elif call_type == 'KaKan':
            self._update_kakan(caller_.hand, mentsu)
        else:
            raise NotImplementedError(
                '%s: %s, %s, %s' % (call_type, caller, callee, convert_hand(mentsu)))

    def _update_kakan(self, hand, mentsu):
        """Update Pon to KaKan

        Parameters
        ----------
        hand : Hand
        mentsu : list of ints
        """
        base = 4 * (mentsu[0] // 4)
        mentsu_ = hand.find_pon(base)
        for tile in mentsu:
            if tile not in mentsu_:
                mentsu_.add(tile)
                hand.closed.remove(tile)
        mentsu_.type = 'KaKan'

    def reach(self, player, step, scores=None):
        """Player declared reach

        Parameters
        ----------
        player : int
        step : int
        scores : list of int or None
        """
        _validate_last_draw(player, self.last_draw['player'])
        player_ = self.players[player]
        if step == 1:
            player_.hand.reach = True
        elif step == 2:
            player_.score -= 1000
            self.state.reach += 1
            if scores:
                _validate_score(self.players, scores)
        else:
            raise NotImplementedError(u'Unexpected step value: %s' % step)

    def agari(self, scores, gains, **data):
        """
        """
        _validate_score(self.players, scores)
        _validate_sticks(self.state, data['ba'])
        _validate_winning_hand(self.players[data['winner']].hand, data)
        if 'loser' in data:
            _validate_furikomi(data['loser'], data['machi'][0], self.last_discard)
        else:
            _validate_last_draw(data['winner'], self.last_draw['player'])

        # skip ten(Fu, Point, limit), yaku, yakuman, dora, ura-dora
        _LG.info(u'Currently, no point conputation is carried out.')

        for player, gain in zip(self.players, gains):
            player.score += gain
        self.state.reach = 0

        if 'result' in data:
            _validate_score(self.players, data['result']['scores'])

    def _process_reach_sticks(self):
        top_players = self._get_top_players()
        if len(top_players) != 1:
            raise NotImplementedError()
        top_players[0].score += 1000 * self.state.reach
        self.state.reach = 0

    def ryuukyoku(self, hands, scores, gains, ba, reason=None, result=None):
        _validate_score(self.players, scores)
        _validate_sticks(self.state, ba)
        _validate_ryuukyoku_hands(self.players, hands)

        for player, gain in zip(self.players, gains):
            player.score += gain

        if reason:
            self.ryuukyoku_reason = reason

        if result:
            if self.state.reach:
                self._process_reach_sticks()
            _validate_score(self.players, result['scores'])

    def bye(self, index):
        self.players[index].available = False

    def resume(self, index, **_):
        self.players[index].available = True


def _validate_round_scores(current_round, previous_round):
    for prev_p, cur_p in zip(previous_round.players, current_round.players):
        if prev_p.score != cur_p.score:
            raise AssertionError(
                (
                    'The previous score does not match to new one. '
                    'Check implementation. Current: %s, Reported: %s'
                ) % (prev_p.score, cur_p.score)
            )


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
            _validate_round_scores(self.round, self.past_rounds[-1])

    def set_uma(self, uma):
        self.uma = uma

    def archive_round(self):
        self.past_rounds.append(self.round)
