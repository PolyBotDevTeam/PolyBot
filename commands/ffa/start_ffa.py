import command_system
import polybot_responses as responses
import utils
import vk_utils


def start_ffa(actor, game_id, game_name, *, database, vk):
    ffa_games = database.ffa_games
    try:
        game = ffa_games.get_game_by_id(game_id)
    except ffa_games.errors.GameNotFoundError:
        return [responses.GAME_NOT_FOUND_ERROR]

    if actor != game.owner_id:
        return [responses.NOT_FFA_OWNER_ERROR]

    try:
        game.start(game_name)
    except game.errors.AlreadyStartedError:
        return [responses.ALREADY_STARTED_ERROR]
    except game.errors.InvalidGameNameError:
        if game_name:
            error_message = responses.INVALID_GAME_NAME_ERROR
        else:
            error_message = responses.EMPTY_GAME_NAME_ERROR
        return [error_message]

    members_mentions = [vk_utils.create_mention(member_id, vk=vk) for member_id in game.members]
    members_mentions = '\n'.join(f'* {mention}' for mention in members_mentions)

    message_about_start = responses.FFA_GAME_STARTED.format(
        game_id=game.id,
        name=game.name,
        members_mentions=members_mentions
    )

    return [message_about_start]


def _process_start_ffa_command(actor, command_text, *, database, vk, **kwargs):
    if not command_text:
        return [responses.START_FFA_NO_ARGUMENTS_ERROR]

    game_id, game_name = utils.split_one(command_text)

    try:
        game_id = int(game_id)
    except ValueError:
        return [responses.INVALID_ID_SYNTAX_ERROR]

    return start_ffa(actor, game_id, game_name, database=database, vk=vk)


start_ffa_command = command_system.Command(
    process=_process_start_ffa_command,
    keys=['начать_ффа', 'начатьффа', 'start_ffa', 'startffa'],
    description='Начать ффа-игру',
    signature='айди_игры название_игры',
    allow_users=True
)
