import collections

import command_system
import message_handler
import vk_utils

import settings


# TODO: page system
def _process_games_command(player_id, command_text, *, database, vk, **kwargs):
    connection = message_handler.create_connection()

    with connection:

        texts_about_games = []

        chat_members_ids = vk_utils.fetch_chat_members_ids(chat_id=settings.main_chat_id, vk=vk)

        for game in _fetch_open_games(database, vk):
            host = game.host
            if host.id not in chat_members_ids:
                continue
            rating_block = f'{host.host_elo} ELO' if game.is_rated else 'UNRATED'
            text_about_game = f'ID: {game.game_id} - {host.username} - {rating_block}\n{game.description}'
            texts_about_games.append(text_about_game)

        limit_per_page = 10
        if len(texts_about_games) == 0:
            messages = ['Не найдено открытых игр. Вы можете открыть новую игру командой /открыть']
        elif len(texts_about_games) <= limit_per_page:
            message = 'Открытые игры:\n\n'
            message += '\n\n'.join(texts_about_games)
            messages = [message]
        else:
            messages = ['Открытые игры:']
            for i_start in range(0, len(texts_about_games), limit_per_page):
                texts_for_current_page = texts_about_games[i_start : i_start+limit_per_page]
                current_page = '\n\n'.join(texts_for_current_page)
                messages.append(current_page)

        messages = [vk_utils.break_mentions(message) for message in messages]

        return messages


_HostInfo = collection.namedtuple('HostInfo', 'id username host_elo')
_OpenGameInfo = collections.namedtuple('OpenGameInfo', 'game_id description is_rated host')


def _fetch_open_games(database, vk):
    db_query = (
        'SELECT games.game_id, games.description, games.is_rated, games.host_id, players.host_elo FROM games '
        'LEFT JOIN players ON players.player_id = games.host_id '
        'WHERE games.type = \'o\' ORDER BY games.time_updated DESC;'
    )

    with database.create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(db_query)
        games_rows = cursor.fetchall()

    host_ids = [host_id for game_id, description, is_rated, host_id, host_elo in games_rows]
    host_usernames = vk_utils.fetch_usernames(host_ids, vk=vk)

    result = []

    for (game_id, description, is_rated, host_id, host_elo), host_username in zip(games_rows, host_usernames):
        host = _HostInfo(host_id, host_username, host_elo)
        result.append(_OpenGameInfo(game_id, description, is_rated, host))

    return result


games_command = command_system.Command(
    process=_process_games_command,
    keys=['игры', 'открытые', 'открытые_игры', 'games', 'open_games'],
    description='Игры к которым можно присоединиться',
    signature='',
    allow_users=True
)
