import command_system
import message_handler


def _all(player_id, command_text):
    args = command_text.split()

    if not args:
        page = 1
    else:
        try:
            [page] = args
            page = int(page)
        except ValueError:
            message = 'После имени команды необходимо ввести номер страницы, которую вы хотите посмотреть. Можно не ввести ничего.'
            return [message]

    connection = message_handler.create_connection()
    with connection:
        message = f'Все игры в системе (страница {page}):\n\n'
        cur = connection.cursor()
        cur.execute('SELECT game_id, name, host_id, away_id, description, host_winner, type FROM games ORDER BY game_id DESC;')
        rows = cur.fetchall()
        if rows:
            count = 0
            for row in rows:
                if count // 10 + 1 == page:
                    if str(row[6]) == 'o':
                        message += 'ID: ' + str(row[0]) + '\n' + message_handler.username(row[2]) + ' vs ___\n' + str(row[4]) + '\n\n'
                    elif str(row[6]) == 'r':
                        message += 'ID: ' + str(row[0]) + ' - ' + str(row[1]) + '\n' + message_handler.username(row[2]) + ' vs ' + message_handler.username(row[3]) + '\n' + str(row[4]) + '\nОжидает начала.' + '\n\n'
                    elif str(row[6]) == 'i':
                        message += 'ID: ' + str(row[0]) + ' - ' + str(row[1]) + '\n' + message_handler.username(row[2]) + ' vs ' + message_handler.username(row[3]) + '\n' + str(row[4]) + '\nВ процессе.' + '\n\n'
                    elif str(row[6]) == 'w':
                        message += 'ID: ' + str(row[0]) + ' - ' + str(row[1]) + '\n' + message_handler.username(row[2]) + ' vs ' + message_handler.username(row[3]) + '\n' + str(row[4]) + '\nПобедитель: ' + message_handler.username(row[3-row[5]]) + '\nОжидает подтверждения.' + '\n\n'
                    elif str(row[6]) == 'c':
                        message += 'ID: ' + str(row[0]) + ' - ' + str(row[1]) + '\n' + message_handler.username(row[2]) + ' vs ' + message_handler.username(row[3]) + '\n' + str(row[4]) + '\nПобедитель: ' + message_handler.username(row[3-row[5]]) + '\n\n'
                count += 1

        messages = [message]
        if page == 1:
            message_about_next_page = f'Для просмотра следующей страницы напишите /все {page+1}'
            messages.append(message_about_next_page)
        return messages


_all_command = command_system.UserCommand()

_all_command.keys = ['все', 'all']
_all_command.description = ' номер_страницы - Список всех игр в системе.'
_all_command.process = _all
