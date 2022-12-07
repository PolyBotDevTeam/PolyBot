def execute(cursor, query, args=None):
    cursor.execute(query, args)
    return cursor


def exists(cursor, table_name, condition, args=None):
    query = f'SELECT * FROM {table_name} WHERE {condition};'
    cursor.execute(query, args)
    return cursor.fetchone() is not None
