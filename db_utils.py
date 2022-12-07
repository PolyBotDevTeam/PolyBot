def execute(cursor, query, args=None):
    cursor.execute(query, args)
    return cursor


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
