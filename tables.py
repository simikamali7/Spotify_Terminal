import sqlite3
import time
import login
import global_file
import sys

connection = global_file.connection
cursor = global_file.cursor
path = str(sys.argv[1])
print(path)
# Get path from command line argument
# path = './prj-test.db'

def connect(path):
    # Connect to the database
    global_file.init(path)
    return

def main():
    global connection, cursor, path
    connect(path)

    # Call user main interface
    login.main_interface()

    connection.commit()
    connection.close()
    return

if __name__ == '__main__':
    main()



# to start up --> go to folder containing all files  - spotify_terminal  --> then input in terminal python3 tables.py project.db
# make sure it is python3 and not python, or else wont work

# to see changes open up database file to see changes reflected.