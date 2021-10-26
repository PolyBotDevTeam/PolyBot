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


def exec_python(player_id, command_text, **kwargs):
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

    def act(command, *, do_act=True):
        def process_exception(e):
            raise e
        response = command_system.process_command(
            -settings.group_id,
            command,
            user_message=None,
            process_exception=process_exception,
            database=kwargs['database'],
            vk=kwargs['vk']
        )
        if do_act:
            for action in response:
                add_action(action)
            del response
        else:
            return response

    def bash(command, do_print=True):
        output = _exec_command_return_output(command)
        if do_print:
            print_to_output(output)
        else:
            return output

    cursor = kwargs['cursor']

    available_globals = {
        'print': print_to_output,
        'add_action': add_action,
        'act': act,
        'bash': bash,

        'kwargs': kwargs,
        'cur': cursor,
        'execute': functools.partial(db_utils.execute, cursor),
        'exists': functools.partial(db_utils.exists, cursor),

        'utils': utils,

        'vk': kwargs['vk'],
        'vk_api': vk_api,

        'mh': message_handler,
        'cs': command_system,
        'getcmd': command_system.get_command,

        'collections': collections,
        'functools': functools,
        'itertools': itertools
    }

    try:
        returned_value = procedure(code, available_globals, None)
    except Exception as e:
        utils.print_exception(e, file=output)
        returned_value = None

    result = output.getvalue()
    if not result or returned_value is not None:
        result += repr(returned_value) + '\n'

    output_messages = [result[i:i+_MAX_MSG_SIZE] for i in range(0, len(result), _MAX_MSG_SIZE)]
    output_messages = [message for message in output_messages if not (isinstance(message, str) and message.isspace())]

    return actions + output_messages


def _exec_command_return_output(command):
    output_filename = _generate_output_filename()
    output_path = os.path.abspath(output_filename)
    os.system(f'{command} > {output_path}')
    with open(output_path) as fp:
        output = fp.read()
    os.remove(output_path)
    return output


def _generate_output_filename():
    digits_n = 12
    output_tag = hex(random.randrange(16**digits_n))[2:].zfill(digits_n)
    return 'command_output_%s.txt' % output_tag


exec_python_command = command_system.Command(
    process=exec_python,
    keys=['exec_python', 'exec_py', 'pyexec', 'py'],
    description='Выполнить указанный код',
    signature='код_на_питоне',
    allow_users=False
)

