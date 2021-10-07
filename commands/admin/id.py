import command_system
import message_handler
import vk_utils


def id(player_id, command_text):
    target = command_text.lstrip()
    if not target:
        return ['Укажите игрока.']

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        try:
            target_id = message_handler.try_to_identify_id(target, cur)
        except vk_utils.InvalidMentionError:
            message = 'Некорректная ссылка. Нажмите @ или * чтобы выбрать среди участников беседы.'
        except ValueError:
            message = 'Никнейм не найден.'
        else:
            message = str(target_id)
        return [message]


command = command_system.AdminCommand()

command.keys = ['id']
command.description = ' игрок - получить айди игрока.'
command.process = id
