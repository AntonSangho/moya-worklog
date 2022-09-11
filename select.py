import sqlite3
from datetime import date

currentDate = date.today()
#print(currentDate)

con = sqlite3.connect('moya.db')
cur = con.cursor()
SelectQuery = """SELECT id, sqltime FROM worklog3 ORDER by rowid DESC LIMIT 1;"""
result = cur.execute(SelectQuery)
rows = result.fetchall()
for row in rows:
    print(row[0])
    print(row[1])

#cur.execute('INSERT INTO worklog (date) VALUES(?)',(currentDateTime))
#con.commit()
#cur.close()
#con.close()
#import sqlite3
#con = sqlite3.connect('otu.db')
#cur = con.cursor()
#result = cur.execute('SELECT * FROM topics')
#rows = result.fetchall()
#for row in rows:
#print(row)
