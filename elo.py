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

    def __str__(self):
        return f'{self.host} : {self.away}'


class MutableELO:

    def __init__(self, host, away):
        self.host = host
        self.away = away

    def to_immutable(self):
        return ELO(self.host, self.away)

    def __iter__(self):
        return iter(self.to_immutable())


elo_base = 10**(1/400)


DEFAULT_ELO = ELO(elo_base**1050, elo_base**950)


# TODO: Move out, this block is not related to elo core

RATING_ROLES = {
    "Новичок": -inf,
    "Стратег": 1100,
    "Мастер": 1200,
    "Легенда": 1300
}

RATING_ROLES_ENABLED = True


HOST_EMOJI = {
    '🟪': 1400,
    '🟩': 1300,
    '🟨': 1200,
    '🟧': 1100,
    '🟫': -inf
}


AWAY_EMOJI = {
    '🟣': 1300,
    '🟢': 1200,
    '🟡': 1100,
    '🟠': 1000,
    '🟤': -inf
}


for _rating_levels_system in [RATING_ROLES, HOST_EMOJI, AWAY_EMOJI]:
    for _rank in _rating_levels_system.keys():
        _rating_levels_system[_rank] = elo_base**_rating_levels_system[_rank]


def _find_best_status_achieved(score, statuses_levels):
    statuses_levels = list(statuses_levels.items())
    statuses_levels.sort(key=lambda kv: kv[1])
    status = None
    for potential_status, score_need in statuses_levels:
        if score >= score_need:
            status = potential_status
    return status


def emoji_by_elo(elo_host, elo_away):
    host_emoji = _find_best_status_achieved(elo_host, HOST_EMOJI)
    away_emoji = _find_best_status_achieved(elo_away, AWAY_EMOJI)
    return host_emoji, away_emoji


# TODO: to hide details, for example can make "EloSystem" class with method "process_game"


def recalculate(*, cur=None):
    if cur is None:
        connection = message_handler.create_connection()
        with connection:
            cur = connection.cursor()
            return recalculate(cur=cur)

    cur.execute('SELECT host_id, away_id, host_winner, is_rated FROM results;')
    games_results = tuple(cur.fetchall())

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner, is_rated in games_results:
        if is_rated:
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
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, is_rated, game_id FROM results;')
    games_times = select(cur, 'SELECT game_id, time_updated FROM games;')
    games_times = dict(games_times)

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    prev_time = None
    for host_id, away_id, host_winner, is_rated, game_id in games_results:
        if is_rated:
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
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, is_rated, game_id FROM results;')

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner, is_rated, game_id in games_results:
        if is_rated:
            elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)
        if game_id == game_id_need:
            break

    return elos


def fetch_rating_deltas(game_id, cur):
    assert isinstance(game_id, int)
    game_id_need = game_id
    del game_id

    recalculate(cur=cur)
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, is_rated, game_id FROM results;')

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner, is_rated, game_id in games_results:
        if game_id == game_id_need:
            old_elos = _compute_final_elo(elos[host_id], games_counts[host_id]).host, _compute_final_elo(elos[away_id], games_counts[away_id]).away

        if is_rated:
            elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)

        if game_id == game_id_need:
            new_elos = _compute_final_elo(elos[host_id], games_counts[host_id]).host, _compute_final_elo(elos[away_id], games_counts[away_id]).away
            return tuple(zip(old_elos, new_elos))

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

    rating = calculate_common_rating(rating)
    role = _find_best_status_achieved(score=rating, statuses_levels=RATING_ROLES)
    return role


def calculate_common_rating(rating):
    return (rating.host * rating.away) ** (1/2)


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
    ea = a / (a + b)
    eb = b / (a + b)
    new_a = a * elo_base ** (50 * (ra - ea))
    new_b = b * elo_base ** (50 * (rb - eb))
    return new_a, new_b


def __old_fetch_elos_changes_history(*, raw=False, cur):
    recalculate(cur=cur)
    games_results = select(cur, 'SELECT host_id, away_id, host_winner, is_rated, game_id FROM results;')
    games_times = select(cur, 'SELECT game_id, time_updated FROM games;')
    games_times = dict(games_times)

    elos = defaultdict(lambda: MutableELO(*DEFAULT_ELO))
    games_counts = defaultdict(lambda: {'host': 0, 'away': 0})

    for host_id, away_id, host_winner, is_rated, game_id in games_results:
        if is_rated:
            elo_process_game(host_id, away_id, host_winner, elos=elos, games_counts=games_counts)
        ids = (host_id, away_id)
        if raw:
            result_elos = tuple(elos[id] for id in ids)
        else:
            result_elos = tuple(_compute_final_elo(elos[id], games_counts[id]) for id in ids)

        time = games_times[game_id]
        yield (time, dict(zip(ids, result_elos)))
