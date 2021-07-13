import builtins
import collections
import functools
import itertools
import io
import os
import random

import vk_api

import command_system
import message_handler
import settings
import utils
import db_utils


_MAX_MSG_SIZE = 4096


def exec_python(player_id, command_text):
    code = command_text.lstrip()
    code = code.replace('~ ~ ', '    ').replace('. . ', '    ')  # TODO: maybe just "empty" char?
    try:
        compile(code, '<string>', 'eval')
    except SyntaxError:
        procedure = exec
    else:
        procedure = eval

    output = io.StringIO()
    def print_to_output(*args, **kwargs):
        if kwargs.get('file') is None:
            kwargs['file'] = output
        builtins.print(*args, **kwargs)

    actions = []
    def add_action(action):
        actions.append(action)

    def act(command, *, cur, do_act=True):
        response = command_system.process_command(-settings.group_id, command, cur)
        if do_act:
            for action in response:
                add_action(action)
            del response
        else:
            return response

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        try:
            vk_session = vk_api.VkApi(token=settings.token)
            returned_value = procedure(
                code,
                {
                    'print': print_to_output,
                    'add_action': add_action,
                    'act': functools.partial(act, cur=cur),
                    'bash': _exec_command_return_output,

                    'cur': cur,
                    'select': functools.partial(db_utils.select, cur),
                    'exists': functools.partial(db_utils.exists, cur),

                    'utils': utils,

                    'vk': vk_session.get_api(),
                    'vk_api': vk_api,

                    'mh': message_handler,
                    'cs': command_system,
                    'getcmd': command_system.get_command,

                    'collections': collections,
                    'functools': functools,
                    'itertools': itertools
                },
                None
            )
        except Exception as e:
            utils.print_exception(e, file=output)
            returned_value = None

    try:
        connection.close()
    except:
        pass

    result = output.getvalue()
    if not result or returned_value is not None:
        result += repr(returned_value) + '\n'
    return actions + [result[i:i+_MAX_MSG_SIZE] for i in range(0, len(result), _MAX_MSG_SIZE)]


def _exec_command_return_output(command):
    output_filename = _generate_output_filename()
    os.system(f'{command} > {output_filename}')
    with open(output_filename) as fp:
        output = fp.read()
    return output


def _generate_output_filename():
    digits_n = 12
    output_tag = hex(random.randrange(16**digits_n))[2:].zfill(digits_n)
    return 'command_output_%s.txt' % output_tag


exec_python_command = command_system.AdminCommand()

exec_python_command.keys = ['exec_python', 'exec_py', 'pyexec', 'py']
exec_python_command.description = ' код на питоне - Выполнить указанный код.'
exec_python_command.process = exec_python

