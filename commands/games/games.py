import command_system
import message_handler
import vk_utils

import settings


# TODO: page system
def _process_games_command(player_id, command_text, *, vk, **kwargs):
    db_query = (
        'SELECT games.game_id, games.description, games.host_id, games.is_rated, players.host_elo FROM games '
        'LEFT JOIN players ON players.player_id = games.host_id '
        'WHERE games.type = \'o\' ORDER BY games.time_updated DESC;'
    )

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute(db_query)
        games_rows = cur.fetchall()

        host_ids = [host_id for game_id, description, host_id, is_rated, host_elo in games_rows]

        host_usernames = vk_utils.fetch_usernames(host_ids, vk=vk)

        texts_about_games = []

        chat_members_ids = vk_utils.fetch_chat_members_ids(chat_id=settings.main_chat_id, vk=vk)

        for (game_id, description, host_id, is_rated, rating), host_username in zip(games_rows, host_usernames):
            if host_id not in chat_members_ids:
                continue
            rating_block = f'{rating} ELO' if is_rated else 'UNRATED'
            text_about_game = f'ID: {game_id} - {host_username} - {rating_block}\n{description}'
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


games_command = command_system.Command(
    process=_process_games_command,
    keys=['игры', 'открытые', 'открытые_игры', 'games', 'open_games'],
    description='Игры к которым можно присоединиться',
    signature='',
    allow_users=True
)
