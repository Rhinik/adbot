from sqlite3 import connect, Row
from typing import List

import attrdict


db_path = "src/db.sqlite3"

# SQLite3 connection
conn = connect(db_path)
conn.row_factory = Row
cursor = conn.cursor()

def get(request, *args) -> List[attrdict.AttrDict]:
    """
    Returns something from database
    """

    ## Get sqlite3.Row objects (there are in a list) and
    ## mapped they to DotDict object
    sql = cursor.execute(request, args)
    sql = sql.fetchall()
    sql = [attrdict.AttrDict(i) for i in sql]

    return sql

def post(request, *args):
    """
    Update and save data in database
    """
    cursor.execute(request, args)
    conn.commit()
