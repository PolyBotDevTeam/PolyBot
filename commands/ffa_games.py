import command_system
import polybot_responses as responses
import vk_utils


def ffa_games(*, database, vk):
    open_ffa_games = database.ffa_games.get_open_games()
    result_text = responses.OPEN_FFA_GAMES_HEADER + '\n\n'
    
    for game in open_ffa_games:
        [owner_username] = vk_utils.fetch_usernames([game.owner_id], vk=vk)
        text_about_game = responses.OPEN_FFA_GAMES_ITEM.format(
            game_id=game.id,
            owner_username=owner_username,
            description=game.description
        )
        result_text += text_about_game + '\n\n'
    
    return [result_text]


def _process_ffa_games_command(actor, command_text, *, database, vk, **kwargs):
    return ffa_games(database=database, vk=vk)


ffa_games_command = command_system.Command(
    process=_process_ffa_games_command,
    keys=[
        'игры_ффа', 'игрыффа',
        'открытые_ффа', 'открытыеффа',
        'games_ffa', 'gamesffa',
        'ffa_games', 'ffagames',
        'open_games_ffa', 'opengamesffa',
        'open_ffa_games', 'openffagames'
    ],
    description='Список ффа-игр, к которым можно присоединиться',
    signature='',
    allow_users=True
)
