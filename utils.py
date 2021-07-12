import builtins as _builtins
import io as _io
import sys as _sys
import traceback as _traceback

import settings as _settings


# TODO: move to vk_utils.py
# TODO: just specify special parameter instead
def delete_mentions(string):
    new_string, *parts = string.split('[')
    for s in parts:
        new_string += '['
        if s.startswith('id'):
            i = 0
            while i < len(s) and s[i] != '|':
                i += 1
            if i == len(s):
                new_string += s[:i]
            else:
                new_string += f'club{_settings.group_id}'
            new_string += s[i:]
    new_string = new_string.replace('all', 'аll').replace('everyone', 'еveryone').replace('online', 'оnline').replace('here', 'hеre')
    new_string = new_string.replace('все', 'вcе').replace('онлайн', 'oнлайн').replace('тут', 'тyт').replace('здесь', 'здeсь')
    return new_string


# split_some?


# TODO: use str.split(..., 1) instead
def split_one(string, sep=None, do_clear_sep=True):
    """Returns two elements.
    The first is the same as string.split(sep)[0].
    The second is remainder.

    Specify do_clear_sep=False if you want to save separator in remainder.
    You can remain separator unspecified.
    """

    try:
        fst = string.split(sep)[0]
    except IndexError:
        raise ValueError('unable to split one, no parts found')

    snd = string[string.index(fst) + len(fst):]
    if do_clear_sep:
        if sep is not None:
            snd = snd[len(sep):]
        else:
            snd = snd.lstrip()

    return fst, snd


def print_exception(e, file=_sys.stdout):
    error_msg_io = _io.StringIO()
    _traceback.print_exception(type(e), e, e.__traceback__, file=error_msg_io)
    _builtins.print(error_msg_io.getvalue(), file=file, flush=True)


def safe_zip(*args):
    args = [tuple(arg) for arg in args]
    if len(set(map(len, args))) > 1:
        raise ValueError('lengths do not match')
    return tuple(zip(*args))
