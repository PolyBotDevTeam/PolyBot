import command_system
import message_handler
import polybot_responses as responses
import utils
import vk_utils


def finish_ffa(actor, game_id, winner_id, *, database, vk):
    ffa_games = database.ffa_games
    try:
        game = ffa_games.get_game_by_id(game_id)
    except ffa_games.errors.GameNotFoundError:
        return [responses.GAME_NOT_FOUND_ERROR]

    if actor != game.owner_id:
        return [responses.NOT_FFA_OWNER_ERROR]

    try:
        game.finish(winner_id)
    except game.errors.NotAMemberError:
        return [responses.WINNER_IS_NOT_A_MEMBER_ERROR]
    except game.errors.NotStartedError:
        return [responses.UNABLE_TO_FINISH_UNSTARTED_GAME]
    except game.errors.AlreadyFinishedError:
        return [responses.ALREADY_FINISHED_ERROR]

    [winner_username] = vk_utils.fetch_usernames([winner_id], vk=vk)

    return [responses.FFA_GAME_FINISHED.format(game_id=game.id, winner_username=winner_username)]


def _process_finish_ffa_command(actor, command_text, *, database, vk, cursor, **kwargs):
    if not command_text:
        return [responses.FINISH_FFA_NO_ARGUMENTS_ERROR]

    game_id, specified_winner = utils.split_one(command_text)

    try:
        game_id = int(game_id)
    except ValueError:
        return [responses.INVALID_ID_SYNTAX_ERROR]

    if not specified_winner:
        return [responses.WINNER_IS_NOT_SPECIFIED_ERROR]

    try:
        winner_id = message_handler.try_to_identify_id(specified_winner, cursor)
    except ValueError:
        return [responses.UNABLE_TO_IDENTIFY_USER]

    return finish_ffa(actor, game_id, winner_id, database=database, vk=vk)


finish_ffa_command = command_system.Command(
    process=_process_finish_ffa_command,
    keys=['завершить_ффа', 'завершитьффа', 'finish_ffa', 'finishffa'],
    description='Завершить ффа-игру',
    signature='айди_игры победитель',
    allow_users=True
)
