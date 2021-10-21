import polybot_database._ffa_game as _ffa_game_module


# TODO: Rename this class
class FFAGames:

    FFAGame = _ffa_game_module.FFAGame
    errors = None  # Will be set later

    def __init__(self, *, execute_query):
        self._execute = execute_query

    def get_game_by_id(self, game_id: int):
        game = self.FFAGame(id=game_id, execute_query=self._execute)
        if not game.exists():
            raise self.errors.GameNotFoundError('the game with this id does not exist')
        return game

    def create_game(self, owner_id: int, description: str, *, is_rated):
        self.FFAGame.verify_description(description)
        self._execute(
            'INSERT ffa_games(owner_id, description, is_rated) VALUES (%s, %s, %s);',
            [owner_id, description, is_rated]
        )

        # TODO: Probably should use LAST_INSERT_ID() to avoid bugs
        [[game_id]] = self._execute('SELECT MAX(game_id) FROM ffa_games;')
        game = self.get_game_by_id(game_id)
        game.add_member(owner_id)
        return game

    # TODO: Add get_all_games() method

    def _select_games(additional_query_part='', args=None):
        response = self._execute(
            f'SELECT game_id FROM ffa_games {additional_query_part};',
            args
        )
        games = (self.get_game_by_id(game_id) for [game_id] in response)
        return games

    def get_open_games(self):
        return self._select_games('WHERE name IS NULL')

    def get_incomplete_games(self):
        return self._select_games('WHERE name IS NOT NULL AND winner_id IS NULL')

    def get_complete_games(self):
        return self._select_games('WHERE winner_id IS NOT NULL')

    def get_games_of_player(self, player_id: int):
        response = self._execute(
            'SELECT game_id FROM ffa_memberships WHERE member_id = %s;',
            [player_id]
        )
        games = (self.get_game_by_id(game_id) for [game_id] in response)
        return games


class _FFAGamesErrors:

    def __init__(self):
        pass

    class GameNotFoundError(ValueError):
        pass

FFAGames.errors = _FFAGamesErrors
