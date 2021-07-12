import command_system
import elo
import message_handler


# TODO: page system
def games(player_id, command_text):
    elo.recalculate()
    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT game_id, host_id, description FROM games WHERE type = \'o\' ORDER BY time_updated ASC;')
        rows = cur.fetchall()
        texts_about_games = []

        for game_id, host_id, description in rows:
            cur.execute('SELECT host_elo FROM players WHERE player_id = %s;', host_id)
            rating = cur.fetchone()[0]
            host_username = message_handler.username(host_id)
            text_about_game = f'ID: {game_id} - {host_username} - {rating} ELO\n{description}'
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

        return messages


games_command = command_system.UserCommand()

games_command.keys = ['игры', 'открытые', 'открытые_игры', 'games', 'open_games']
games_command.description = ' - Игры к которым можно присоединиться'
games_command.process = games
