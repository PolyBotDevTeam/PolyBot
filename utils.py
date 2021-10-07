import builtins as _builtins
import io as _io
import sys as _sys
import traceback as _traceback

# TODO: Should remove block with delete_mentions, it's only here for backward compatibility
import vk_utils as _vk_utils


delete_mentions = _vk_utils.break_mentions


# TODO: split_some?

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


def represent_exception(e):
    error_msg_io = _io.StringIO()
    _traceback.print_exception(type(e), e, e.__traceback__, file=error_msg_io)
    return error_msg_io.getvalue()


def print_exception(e, file=_sys.stdout):
    error_msg = represent_exception(e)
    _builtins.print(error_msg, file=file, flush=True)


def safe_zip(*args, result_length=None):
    args = [tuple(arg) for arg in args]

    length_variants = set(map(len, args))
    if len(length_variants) > 1:
        raise ValueError('arguments lengths do not match')

    if result_length is not None:
        length_variants.add(result_length)

    if len(length_variants) > 1:
        raise ValueError('arguments lengths do not match with specified result length')
    elif not length_variants:
        raise ValueError('can\'t determine result length without arguments')

    [result_length] = length_variants

    result = tuple(zip(*args))
    if len(result) != result_length:
        assert not result and not args
        result = tuple(() for i in range(result_length))

    return result
