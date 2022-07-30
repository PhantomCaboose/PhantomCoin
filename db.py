import sqlite3

with open('build.sql', 'r') as sql_file:
    sql_script = sql_file.read()

conn = sqlite3.connect("postgres://nmcgdfkyvqgeaw:79bcf300c4575721be55517cf9b0cd72bc929faddd6318c12152e0f75b2d41cb@ec2-44-206-197-71.compute-1.amazonaws.com:5432/d9s5shn5b38h5j", check_same_thread = False)
cursor = conn.cursor()
cursor.executescript(sql_script)
cursor.close()