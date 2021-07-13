# TODO: deprecated
def select(cursor, query, args=None):
    cursor.execute(query, args)
    return tuple( cursor.fetchall() )


def execute(cursor, query, args=None):
    cursor.execute(query, args)
    return cursor


# TODO: replace deprecated select with this
def new_select(cursor, params, table_name, condition=None, args=None):
    condition_part = f' WHERE {condition}' if condition is not None else ''
    query = f'SELECT {params} FROM {table_name}{condition_part};'
    cursor.execute(query, args)
    return cursor.fetchall()
del new_select


def exists(cursor, table_name, condition, args=None):
    query = f'SELECT * FROM {table_name} WHERE {condition};'
    response = select(cursor, query, args)
    return len(response) > 0


"""
def exists(cursor, table_name, condition, args=None):
    response = new_select(cursor, '*', table_name, condition, args)
    return len(response) > 0


class PyMySQLWrapper:

    def execute(self, query, args):
        pass
"""
