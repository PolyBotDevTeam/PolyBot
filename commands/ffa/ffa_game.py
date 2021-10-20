import command_system
import polybot_responses as responses
import vk_utils


def view_ffa_game(game_id, *, database, vk):
    ffa_games = database.ffa_games
    try:
        game = ffa_games.get_game_by_id(game_id)
    except ffa_games.errors.GameNotFoundError:
        return [responses.GAME_NOT_FOUND_ERROR]

    [owner_username] = vk_utils.fetch_usernames([game.owner_id], vk=vk)
    members_usernames = vk_utils.fetch_usernames(game.members, vk=vk)
    members_usernames_lines = '\n'.join(f'* {username}' for username in members_usernames)
    formatting_params = {
        'game_id': game.id,
        'description': game.description,
        'owner_username': owner_username,
        'members_usernames': members_usernames_lines,
        'is_rated_info': responses.GAME_IS_RATED if game.is_rated() else responses.GAME_IS_UNRATED
    }

    if game.is_started():
        formatting_params['name'] = game.name

    if game.is_finished():
        winner_username = vk_utils.fetch_username(game.winner_id, vk=vk)
        formatting_params['winner_username'] = winner_username

    if game.is_finished():
        template = responses.FINISHED_FFA_GAME_INFO
    elif game.is_started():
        template = responses.STARTED_FFA_GAME_INFO
    else:
        template = responses.OPEN_FFA_GAME_INFO

    game_info = template.format(**formatting_params)

    return [game_info]


def _process_ffa_game_command(actor, command_text, *, database, vk, **kwargs):
    if not command_text:
        return [responses.MISSING_ID_ERROR]
    try:
        game_id = int(command_text)
    except ValueError:
        return [responses.INVALID_ID_SYNTAX_ERROR]
    return view_ffa_game(game_id=game_id, database=database, vk=vk)


ffa_game_command = command_system.Command(
    process=_process_ffa_game_command,
    keys=[
        'игра_ффа', 'играффа',
        'ффа_игра', 'ффаигра',
        'game_ffa', 'gameffa',
        'ffa_game', 'ffagame'
    ],
    description='Посмотреть информацию об ффа-игре',
    signature='айди_игры',
    allow_users=True
)
