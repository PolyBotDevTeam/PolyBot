from collections import defaultdict
from math import inf

import message_handler
from db_utils import select



# EloSystem:
#     __init__
#     insert_result?
#     edit_result?
#     set_result?  # TODO: bad method?
#     set_win?
#     delete_result


# TODO: make private everything non-public


class ELO:

    def __init__(self, host, away):
        self.__host = host
        self.__away = away

    def __eq__(self, other):
        return self.host == other.host and self.away == other.away

    @property
    def host(self):
        return self.__host

    @property
    def away(self):
        return self.__away

    def __iter__(self):
        return iter((self.host, self.away))

    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = ELO(other, other)
        return ELO(self.host + other.host, self.away + other.away)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = ELO(other, other)
        return ELO(self.host - other.host, self.away - other.away)


class MutableELO:

    def __init__(self, host, away):
        self.host = host
        self.away = away

    def to_immutable(self):
        return ELO(self.host, self.away)

    def __iter__(self):
        return iter(self.to_immutable())


DEFAULT_ELO = ELO(1050, 950)


RATING_ROLES = {
    "Новичок": -inf,
    "Стратег": 1100,
    "Мастер": 1200,
    "Легенда": 1300
}

RATING_ROLES_ENABLED = True


# TODO: to hide details, for example can make "EloSystem" class with method "process_game"


def recalculate(*, cur=None):
    if cur is None:
        connection = message_handler.create_connection()
        with connection:
            cur = connection.cursor()
            return recalculate(cur=cur)

    cur.execute('SELECT host_id, away_id, host_winner FROM results;')
    games_results = tuple(cur.fetchall())

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner in games_results:
        elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)

    roles = dict()
    cur.execute('SELECT player_id, role, banned FROM players;')
    for player_id, role, banned in cur.fetchall():
        roles[player_id] = _compute_role(role, elos[player_id], games_counts[player_id], banned)

    cur.execute('SELECT player_id, host_elo, elo, role FROM players;')
    players_rows = cur.fetchall()
    for player_id, old_host_elo, old_away_elo, old_role in tuple(players_rows):
        p_id = player_id
        host_elo, away_elo = _compute_final_elo(elos[p_id], games_counts[p_id])
        role = roles[p_id]
        if (round(host_elo), round(away_elo), role) != (old_host_elo, old_away_elo, old_role):
            cur.execute(
                'UPDATE players SET host_elo = %s, elo = %s, role = %s WHERE player_id = %s;',
                (host_elo, away_elo, role, player_id)
            )


def elo_process_game(host_id, away_id, host_winner, *, elos, games_counts):
    elo_a = elos[host_id].host
    elo_b = elos[away_id].away
    new_a, new_b = new_rating(elo_a, elo_b, host_winner)
    elos[host_id].host = new_a
    elos[away_id].away = new_b
    games_counts[host_id]['host'] += 1
    games_counts[away_id]['away'] += 1


# TODO: insert_result
#       remove_result


def fetch_elos_changes_history(*, raw=False, cur):
    recalculate(cur=cur)
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, game_id FROM results;')
    games_times = select(cur, 'SELECT game_id, time_updated FROM games;')
    games_times = dict(games_times)

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    prev_time = None
    for host_id, away_id, host_winner, game_id in games_results:
        elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)
        ids = (host_id, away_id)
        if raw:
            result_elos = tuple(elos[id] for id in ids)
        else:
            result_elos = tuple(_compute_final_elo(elos[id], games_counts[id]) for id in ids)

        time = games_times[game_id]
        if prev_time is not None:
            time = max(time, prev_time)
        prev_time = time
        yield (time, dict(zip(ids, result_elos)))


def compute_old_ratings(game_id, *, cur):
    assert isinstance(game_id, int)
    game_id_need = game_id
    del game_id

    recalculate(cur=cur)
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, game_id FROM results;')

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner, game_id in games_results:
        elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)
        if game_id == game_id_need:
            break

    return elos


def fetch_rating_deltas(game_id, cur):
    assert isinstance(game_id, int)
    game_id_need = game_id
    del game_id

    recalculate(cur=cur)
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, game_id FROM results;')

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner, game_id in games_results:
        if game_id == game_id_need:
            old_elos = _compute_final_elo(elos[host_id], games_counts[host_id]).host, _compute_final_elo(elos[away_id], games_counts[away_id]).away
            elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)
            new_elos = _compute_final_elo(elos[host_id], games_counts[host_id]).host, _compute_final_elo(elos[away_id], games_counts[away_id]).away
            return tuple(zip(old_elos, new_elos))

        elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)

    raise ValueError("game with such id not found")


def describe_rating_changes(game_id, *, cur):
    ((host_id, away_id),) = select(cur, 'SELECT host_id, away_id FROM games WHERE game_id = %s;', game_id)
    deltas = fetch_rating_deltas(game_id, cur)
    changes_desc = "%s: %s\n%s: %s" % (
        message_handler.username(host_id), _get_change_desc(*deltas[0]),
        message_handler.username(away_id), _get_change_desc(*deltas[1])
    )
    return changes_desc


def _get_change_desc(old_rating, new_rating):
    delta = new_rating - old_rating
    old_rating = round(old_rating)
    new_rating = round(new_rating)
    if delta > 0:
        sign = '+'
    elif delta == 0:
        sign = ''
    else:
        sign = '-'
    delta_abs = abs(delta)
    return "%s -> %s (%s%d)" % (old_rating, new_rating, sign, round(delta_abs))


def _compute_final_elo(elo_pair, games_counts_pair):
    host_games = games_counts_pair['host']
    away_games = games_counts_pair['away']
    host_elo = elo_pair.host  # - (DEFAULT_ELO.host/50 // 2**host_games) * 50
    away_elo = elo_pair.away  # - (DEFAULT_ELO.away/50 // 2**away_games) * 50
    return ELO(host_elo, away_elo)


DEFAULT_FINAL_ELO = _compute_final_elo(DEFAULT_ELO, {'host': 0, 'away': 0})


def _compute_role(old_role, rating, games_counts, banned):
    assert isinstance(rating, (ELO, MutableELO))

    if banned:
        return 'Banned'
    if old_role not in RATING_ROLES.keys() and old_role is not None and old_role != 'Banned':
        return old_role
    del banned, old_role

    if not RATING_ROLES_ENABLED:
        return None

    rating = sum(rating) / 2
    roles = list(RATING_ROLES.items())
    roles.sort(key=lambda kv: kv[1])
    role = None
    for potential_role, rating_need in roles:
        if rating >= rating_need:
            role = potential_role
    return role


def new_rating(a, b, result):
    if result is None:
        ra = 1/2
        rb = 1/2
    elif result:
        ra = 1
        rb = 0
    else:
        ra = 0
        rb = 1
    ea = 1 / (1 + 10**((b - a) / 400))
    eb = 1 / (1 + 10**((a - b) / 400))
    new_a = a + 50 * (ra - ea)
    new_b = b + 50 * (rb - eb)
    return new_a, new_b


def __old_fetch_elos_changes_history(*, raw=False, cur):
    recalculate(cur=cur)
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, game_id FROM results;')
    games_times = select(cur, 'SELECT game_id, time_updated FROM games;')
    games_times = dict(games_times)

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner, game_id in games_results:
        elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)
        ids = (host_id, away_id)
        if raw:
            result_elos = tuple(elos[id] for id in ids)
        else:
            result_elos = tuple(_compute_final_elo(elos[id], games_counts[id]) for id in ids)

        time = games_times[game_id]
        yield (time, dict(zip(ids, result_elos)))
