def execute(cursor, query, args=None, *, lazy_result=False):
    cursor.execute(query, args)
    result_items = cursor
    if not lazy_result:
        result_items = tuple(result_items)
    return result_items


def exists(cursor, table_name, condition, args=None):
    query = format_identifiers('SELECT * FROM {table_name}', table_name=table_name)
    query += f' WHERE {condition};'
    cursor.execute(query, args)
    return cursor.fetchone() is not None


def format_identifiers(query, *args, **kwargs):
    args = [_escape_identifier(identifier) for identifier in args]
    kwargs = {key: _escape_identifier(identifier) for key, identifier in kwargs.items()}
    return query.format(*args, **kwargs)


def _escape_identifier(identifier):
    return '`' + identifier.replace('`', '``') + '`'
