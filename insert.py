import sqlite3
import datetime

#now = datetime.datetime.now()
#print('now', now)
#
#nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
#print('nowDatetime', nowDatetime)

con = sqlite3.connect('moya.db')
cur = con.cursor()
#insertQuery = """INSERT INTO 'worklog'(date) VALUES(?);"""
#cur.execute(insertQuery,('select datetime ('now', 'localtime')'))
cur.execute("INSERT INTO worklog3 ('number') VALUES('null')")
con.commit()
cur.close()
con.close()
