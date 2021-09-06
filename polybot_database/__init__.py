import warnings

import polybot_database._players as _players_module
import polybot_database._ffa_games as _ffa_games_module


# TODO: should also create database.players, database.games etc.


class PolyBotDatabase:

    # TODO: probably should take execute_query argument
    #       instead of create_connection
    def __init__(self, create_connection):
        self._create_connection = create_connection
        self._ffa_games = _ffa_games_module.FFAGames(execute_query=self._execute_query)
        self._players = _players_module.Players(execute_query=self._execute_query)

    @property
    def create_connection(self):
        warnings.warn(
            'PolyBotDatabase.create_connection is deprecated '
            'and will be removed in the future.',
            DeprecationWarning
        )
        return self._create_connection

    def _execute_query(self, query, args=None):
        # The reason why should create a new connection:
        # it's bad idea to use the same connection for all queries
        # https://stackoverflow.com/questions/14827783/auto-increment-and-last-insert-id/14827987#14827987
        # Another reason - it's the simplest way to avoid this:
        # https://dev.mysql.com/doc/refman/5.7/en/gone-away.html
        connection = self._create_connection()
        cursor = connection.cursor()
        cursor.execute(query, args)
        return cursor

    @property
    def ffa_games(self):
        return self._ffa_games

    @property
    def players(self):
        return self._players
