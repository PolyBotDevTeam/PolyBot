import functools
import itertools
import io

import vk_api

import matplotlib.pyplot as plt
import matplotlib

import command_system
from vk_actions import Message

import elo
import message_handler
from db_utils import select, exists

import settings


def rating_graph(player_id, command_text):
    command_text = command_text.lstrip()
    pointer = command_text if command_text else None

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        try:
            if pointer is not None:
                target_id = message_handler.try_to_identify_id(pointer, cur)
            else:
                target_id = player_id
            del player_id
        except ValueError:
            return ['Не удалось найти страницу пользователя по введённым данным.']

        if not exists(cur, 'players', 'player_id = %s', target_id):
            message = 'Этот пользователь ещё не зарегистрирован в системе.'
            return [message]

        changes_history = elo.fetch_elos_changes_history(cur=cur)
        changes_history = tuple(changes_history)
        ((joining_time,),) = select(cur, 'SELECT joining_time FROM players WHERE player_id = %s;', target_id)
        ((now,),) = select(cur, 'SELECT NOW();')

    host_elos = [elo.DEFAULT_ELO.host]
    away_elos = [elo.DEFAULT_ELO.away]
    times = [joining_time]
    for (time, changes) in changes_history:
        for player_id in changes.keys():
            if player_id == target_id:
                host_elo, away_elo = changes[player_id]
                times.append(time)
                host_elos.append(host_elo)
                away_elos.append(away_elo)

    username = message_handler.username(target_id)
    image_common = build_graph(times, host_elos, away_elos, now, title='Рейтинг игрока "%s"' % username)
    # image_host = build_graph(times, host_elos, remove_repeating=True, title='Рейтинг игрока "%s" (хост)' % username)
    # image_away = build_graph(times, away_elos, remove_repeating=True, title='Рейтинг игрока "%s" (второй)' % username)

    vk_session = vk_api.VkApi(token=settings.token)
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk)

    photos = upload.photo_messages([image_common])  # , image_host, image_away])
    photos = ['photo{owner_id}_{id}'.format(**photo) for photo in photos]
    result = [
        Message(attachments=[photos[0]])
        # Message(attachments=photos[1:])
    ]
    return result


def _fix_times(times):
    return tuple(itertools.accumulate(times, max))


# TODO: possible memory leak
def build_graph(datetimes, hosts_elos, aways_elos, now, *, title=None):
    datetimes = list(datetimes)
    hosts_elos = list(hosts_elos)
    aways_elos = list(aways_elos)

    datetimes.append(now)
    hosts_elos.append(hosts_elos[-1])
    aways_elos.append(aways_elos[-1])

    datetimes = _fix_times(datetimes)

    dates = matplotlib.dates.date2num(datetimes)
    del datetimes

    plt.style.use('dark_background')
    fig, ax = plt.subplots()

    ax.set_ylim((700, 1550))

    """ax.plot_date(dates, values, fmt='-', color=(0, 0.5, 0.8))
    ax.plot_date(dates, values, fmt='o', markersize=2.5, color=(0.8, 0.8, 0.8), alpha=1)"""

    # ax.plot_date(dates, common_elos, fmt='-', color=(0.3, 0.3, 0.3))
    # ax.plot_date(dates, common_elos, fmt='o', markersize=1.5, color=(0.85, 0.85, 0.85), alpha=1)

    rem_dup = functools.partial(_remove_duplicate_neighbors, save_last=True)
    host_point = away_point = (0.75, 0.75, 0.75)

    # alpha = 0.5 (if secondary)

    away_color = (0, 0.5, 0)
    away_points = [list(seq) for seq in rem_dup(dates, aways_elos)]
    ax.plot_date(*away_points, fmt='-', color=away_color, alpha=1)
    away_points[0].pop()
    away_points[1].pop()
    ax.plot_date(*away_points, fmt='o', markersize=1.5, color=away_point, alpha=1)
    del away_points

    host_color = (0.6, 0.6, 0)
    host_points = [list(seq) for seq in rem_dup(dates, hosts_elos)]
    ax.plot_date(*host_points, fmt='-', color=host_color, alpha=1)
    host_points[0].pop()
    host_points[1].pop()
    ax.plot_date(*host_points, fmt='o', markersize=1.5, color=host_point, alpha=1)
    del host_points

    fig.autofmt_xdate()

    ax.fmt_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d')
    if title is not None:
        ax.set_title(title)

    ax.grid(color=(0.1, 0.1, 0.1))

    output = io.BytesIO()
    fig.savefig(output)
    return io.BytesIO(output.getvalue())


def _remove_duplicate_neighbors(xs, ys, *, save_last=False):
    points = list(zip(xs, ys))
    points = [pos for i, pos in enumerate(points) if i == 0 or pos[1] != points[i-1][1] or (save_last and i == len(points)-1)]
    xs, ys = zip(*points)
    return xs, ys


rating_graph_command = command_system.UserCommand()

rating_graph_command.keys = ['рейтинг', 'график', 'rating', 'rating_graph', 'graph']
rating_graph_command.description = ' игрок - История рейтинга пользователя.'
rating_graph_command.process = rating_graph
