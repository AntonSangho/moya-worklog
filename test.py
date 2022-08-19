import sqlite3
import datetime

now = datetime.datetime.now()
print('now', now)

nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
print('nowDatetime', nowDatetime)

con = sqlite3.connect('moya.db')
cur = con.cursor()
#insertQuery = """INSERT INTO 'worklog'(date) VALUES(?);"""
#cur.execute(insertQuery,'nowDatetime')
cur.execute("INSERT INTO worklog (date) VALUES(?)",(nowDatetime))
con.commit()
cur.close()
con.close()
#import sqlite3
#con = sqlite3.connect('otu.db')
#cur = con.cursor()
#result = cur.execute('SELECT * FROM topics')
#rows = result.fetchall()
#for row in rows:
#print(row)
