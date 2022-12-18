import command_system
import command_parsing_utils
import vk_utils


def _process_id_command(player_id, command_text, *, database, vk, **kwargs):
    target = command_text.lstrip()
    if not target:
        return ['Укажите игрока.']

    connection = database.create_connection()
    with connection:
        cur = connection.cursor()
        try:
            target_id = command_parsing_utils.try_to_identify_id(target, cur, vk=vk)
        except vk_utils.InvalidMentionError:
            message = 'Некорректная ссылка. Нажмите @ или * чтобы выбрать среди участников беседы.'
        except ValueError:
            message = 'Никнейм не найден.'
        else:
            message = str(target_id)
        return [message]


command = command_system.Command(
    process=_process_id_command,
    keys=['id'],
    description='Получить айди игрока',
    signature='игрок',
    allow_users=False
)
