import datetime

import command_system


def _process_nut_command(actor_id, command_text, **kwargs):
    if _is_nut_sticker_allowed_now():
        yield from _send_nut_sticker(kwargs)
    else:
        yield 'Команда заблокирована до первого декабря.'


def _send_nut_sticker(kwargs):
    nut_sticker_id = 163
    vk = kwargs['vk']
    peer_id = kwargs['actor_message']['peer_id']
    vk.messages.send(sticker_id=nut_sticker_id, peer_id=peer_id, random_id=0)
    if False:
        yield


def _is_nut_sticker_allowed_now():
    polybot_timezone = datetime.timezone(datetime.timedelta(hours=+3))
    datetime_now = datetime.datetime.now(polybot_timezone)
    return datetime_now.month != 11


_ru_keys = ('орех',)
_en_keys = ('opex', 'nut')


nut_command = command_system.Command(
    process=_process_nut_command,
    keys=_ru_keys + _en_keys,
    description='Навести справедливость в чате',
    signature='',
    allow_users=True
)
