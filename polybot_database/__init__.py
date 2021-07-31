import warnings

import polybot_database._ffa_games as _ffa_games_module


# TODO: should also create database.players, database.games etc.


class PolyBotDatabase:

    # TODO: probably should take execute_query argument
    #       instead of create_connection
    def __init__(self, create_connection):
        self._create_connection = create_connection
        self._connection = self._create_connection()
        self._ffa_games = _ffa_games_module.FFAGames(execute_query=self._execute_query)

    @property
    def create_connection(self):
        warnings.warn(
            'PolyBotDatabase.create_connection is deprecated '
            'and will be removed in the future.',
            warnings.DeprecationWarning
        )
        return self._create_connection

    def _execute_query(self, query, args):
        # TODO: probably should also create new connection here
        #       Reason: https://stackoverflow.com/questions/14827783/auto-increment-and-last-insert-id/14827987#14827987
        cursor = self._connection.cursor()
        cursor.execute(query, args)
        return cursor

    @property
    def ffa_games(self):
        return self._ffa_games
