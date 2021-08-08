import utils as _utils


class FFAGame:

    def __init__(self, *, game_id: int, execute_query):
        self._execute = execute_query
        self._game_id = game_id  # TODO: Probably should rename to just self._id
        self._errors = _FFAGameErrors()
        # TODO: Probably should add _ensure_exists

    @property
    def errors(self):
        return self._errors

    def exists(self):
        [[does_exist]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_games WHERE game_id = %s);',
            [self._game_id]
        )
        return does_exist

    def add_player(self, player_id: int):
        if self.has_member(player_id):
            raise self.errors.AlreadyMemberError('this player has already joined the game')
        self._execute(
            'INSERT ffa_memberships(member_id, game_id) VALUES (%s, %s);',
            [player_id, self._game_id]
        )

    def remove_player(self, player_id: int):
        if not self.has_member(player_id):
            raise self.errors.NotAMemberError('this player is not in the game')
        self._execute(
            'DELETE FROM ffa_memberships WHERE member_id = %s AND game_id = %s;',
            [player_id, self._game_id]
        )

    def has_member(self, player_id: int):
        [[result]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_memberships WHERE member_id = %s AND game_id = %s);',
            [player_id, self._game_id]
        )
        return result

    # Probably should not use "id" in the method name
    # because it sounds more like implementation detail.
    # It's easier to think about abstract members rather than their ids.
    def get_members(self):
        response = self._execute(
            'SELECT member_id FROM ffa_memberships WHERE game_id = %s;',
            self._game_id
        )
        [members_ids] = _utils.safe_zip(*response)
        return members_ids

    def start(self, game_name: str):
        raise NotImplementedError

    def finish(self, winner_id: int):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class _FFAGameErrors:

    def __init__(self):
        pass

    class AlreadyMemberError(ValueError):
        pass

    class NotAMemberError(ValueError):
        pass
