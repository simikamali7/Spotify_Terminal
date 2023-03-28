import tables
import sqlite3
import sys

def init(path):
    # This function connects to the database
    global connection
    global cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return(cursor,connection)

path = str(sys.argv[1])
# path = './prj-test.db'
(cursor,connection) = init(path)
# defines a global variable to all the documents within the folder

# print(cursor,connection)