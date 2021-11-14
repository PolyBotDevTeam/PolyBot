from abc import ABCMeta, abstractmethod
import random

from settings import admins_ids, errors_log_file
from utils import split_one, print_exception
import vk_actions

import user_errors  # need we this?


# TODO: get rid of global vars and use autoimports instead
#       (but probably it is not good idea to import fixed name)
#       Maybe .register instead?
# TODO: register_command()?


class Command:

    def __init__(self, *, process, keys, description, signature, allow_users):
        self._process = process
        self._keys = tuple(keys)
        self._description = str(description)
        self._signature = str(signature)
        self._allow_users = bool(allow_users)
        self._command_list.add(self)

    def __call__(self, actor, command_text, **kwargs):
        return self._process(actor, command_text, **kwargs)

    @property
    def _command_list(self):
        return user_commands if self._allow_users else admin_commands

    @property
    def keys(self):
        return self._keys

    # Deprecated
    @property
    def description(self):
        signature = ' ' + self._signature if self._signature else ''
        description = self._description
        return f'{signature} - {description}'


# Several ideas
"""class Command:

    __init__:
        # TODO: admin_chats
        # TODO: self.__prefix = None

    compose_description(self, command_name_to_use=None):
        if command_name_to_use is None:
            command_name_to_use = self.keys[0]
        return self.__prefix + command_name_to_use + self.__description"""


class CommandsList:

    def __init__(self):
        self._commands_list = []
        self._commands_by_keys = dict()

    def add(self, command):
        keys = tuple(command.keys)

        conflict_keys = set(keys) & self._commands_by_keys.keys()
        if conflict_keys:
            raise ValueError('keys conflict: %s' % sorted(conflict_keys))

        self._commands_list.append(command)
        for key in keys:
            self._commands_by_keys[key] = command

    def remove(self, command):
        try:
            self._commands_list.remove(command)
        except ValueError:
            raise CommandNotFoundError

        for k, v in list(self._commands_by_keys.items()):
            if v == command:
                del self._commands_by_keys[k]

    def __contains__(self, command):
        return command in self._commands_list

    def update_keys(self, command):
        self.remove(command)
        self.add(command)

    def get_command(self, key):
        try:
            result = self._commands_by_keys[key]
        except KeyError:
            raise CommandNotFoundError
        else:
            return result

    def has_command(self, key):
        return key in self._commands_by_keys.keys()

    def __iter__(self):
        return iter(self._commands_list)


class CommandNotFoundError(KeyError):
    pass


user_commands = CommandsList()
admin_commands = CommandsList()

def get_user_command_list():
    return list(user_commands)


def parse_command(command_str):
    prefix = command_str[:1]
    command_body = command_str[len(prefix):]
    command_name, command_text = split_one(command_body)
    command_name = command_name.lower()
    return prefix, command_name, command_text


def _process_user_command(actor_id, command_as_string, connection, **kwargs):
    prefix, command_name, command_text = parse_command(command_as_string)
    assert prefix == '/'

    if _is_banned(actor_id, connection):
        return ['С лёгким паром!']
    assert not _is_banned(actor_id, connection)

    if not user_commands.has_command(command_name):
        return ['Команда не распознана. Напишите "/помощь", чтобы получить список команд.']
    cmd = user_commands.get_command(command_name)

    return cmd(actor_id, command_text, **kwargs)


def _is_banned(user_id, connection):
    cursor = connection.cursor()
    cursor.execute('SELECT EXISTS(SELECT player_id FROM players WHERE player_id = %s AND banned = 1)', user_id)
    return bool(cursor.fetchone()[0])


def _process_admin_command(actor_id, command_as_string, connection, **kwargs):
    prefix, command_name, command_text = parse_command(command_as_string)
    assert prefix == '!'

    if not admin_commands.has_command(command_name):
        return []
    cmd = admin_commands.get_command(command_name)

    if actor_id in admins_ids:
        assert actor_id in admins_ids
        result = cmd(actor_id, command_text, **kwargs)
    else:
        text = 'Отказано в доступе.'
        if 'py' in cmd.keys:
            text += '\n'
            text += '0x' + hex(random.randrange(16**8))[2:].zfill(8)
        result = [text]

    return result


def process_command(user_id, command_str, user_message, *, process_exception, database, vk):
    prefix, command_name, command_text = parse_command(command_str)
    if prefix == '/':
        process = _process_user_command
    else:
        process = _process_admin_command

    accumulated_responses = []
    def send_action(action):
        accumulated_responses.append(action)

    available_objects = {
        'send_action': send_action,
        'actor_message': user_message,
        'database': database,
        'vk': vk
    }

    def _command_responses_to_actions(responses):
        for response in responses:
            if isinstance(response, vk_actions.Action):
                action = response
            else:
                assert isinstance(response, str)
                action = vk_actions.Message(text=str(response))
            yield action

    try:
        with database.create_connection() as connection:
            responses = process(
                user_id, command, connection,
                cursor=connection.cursor(), **available_objects
            )
            for response in responses:
                accumulated_responses.append(response)
                yield from _command_responses_to_actions(accumulated_responses)
                accumulated_responses.clear()

    except Exception as e:
        if isinstance(e, user_errors.UserError):
            messages = [str(text) for text in e.args]
            if not messages:
                messages.append('Неправильный формат ввода.')
            print_exception(e, file=errors_log_file)
        else:
            messages = ['Что-то пошло не так.']
            process_exception(e)
        accumulated_responses.extend(messages)

    yield from _command_responses_to_actions(accumulated_responses)
    accumulated_responses.clear()


def get_command(command_str):
    if not command_str:
        raise ValueError('empty string given as command')

    prefix, command_name, command_text = parse_command(command_str)

    if prefix not in ('/', '!'):
        raise ValueError('unknown prefix')

    if command_text:
        raise ValueError('should not specify command text')

    commands = user_commands if prefix == '/' else admin_commands
    return commands.get_command(command_name)


# Deprecated


class CommandAbstract(metaclass=ABCMeta):

    def __init__(self):
        self.__keys = []
        self.description = ''
        self._command_list.add(self)

    def __call__(self, actor, command_text, **kwargs):
        return self.process(actor, command_text)

    # or maybe
    # def __call__(self, actor, command_text, other_params):
    #     return self.process(actor, command_text)

    @property
    @abstractmethod
    def _command_list(self):
        pass

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, mas):
        self.__keys[:] = [k.lower() for k in mas]
        self._command_list.update_keys(self)

    def process(self):
        pass


class UserCommand(CommandAbstract):
    @property
    def _command_list(self):
        return user_commands


class AdminCommand(CommandAbstract):
    @property
    def _command_list(self):
        return admin_commands
