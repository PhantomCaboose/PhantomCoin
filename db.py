import sqlite3

with open('build.sql', 'r') as sql_file:
    sql_script = sql_file.read()

conn = sqlite3.connect("crypto.sqlite", check_same_thread = False)
cursor = conn.cursor()
cursor.executescript(sql_script)
cursor.close()