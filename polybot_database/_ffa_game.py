import utils as _utils


class FFAGame:

    def __init__(self, *, game_id, execute_query):
        self._execute = execute_query
        self._game_id = game_id
        self._errors = _FFAGameErrors()
        # TODO: Probably should add _ensure_exists

    @property
    def errors(self):
        return self._errors

    def exists(self):
        raise NotImplementedError

    def add_player(self, player_id):
        if self.has_member(player_id):
            raise self.errors.AlreadyMemberError('this player has already joined the game')
        self._execute(
            'INSERT ffa_memberships(member_id, game_id) VALUES (%s, %s);',
            [player_id, game_id]
        )

    def remove_player(self, player_id):
        if not self.has_member(player_id):
            raise self.errors.NotMemberError('this player is not in the game')
        self._execute(
            'DELETE FROM ffa_memberships WHERE member_id = %s AND game_id = %s;',
            [player_id, game_id]
        )

    def has_member(self, player_id):
        [[result]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_memberships WHERE member_id = %s AND game_id = %s);'
            [player_id, game_id]
        )
        return result

    # Probably should not use "id" in the method name
    # because it sounds more like implementation detail.
    # It's easier to think about abstract members rather than their ids.
    def get_members(self):
        response = self._execute(
            'SELECT member_id FROM ffa_memberships WHERE game_id = %s;',
            game_id
        )
        [members_ids] = _utils.safe_zip(*response)
        return members_ids

    def start(self, game_name):
        raise NotImplementedError

    def finish(self, winner_id):
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
