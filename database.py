

import sqlite3 as sql


class DataBase():
	
	def __init__(self):
		try:
			self.conn=sql.connect('feedback.db')
			self.conn.execute("create table feedback (FName char[25], LName char[25], Email char[40], query char[200] ); ")
		except:
			pass
	
	def Add(self,data):
		cmd=f"INSERT INTO feedback VALUES ('{ data[0] }', '{ data[1] }', '{ data[2] }', '{ data[3] }');"
		self.conn.execute(cmd)
		self.conn.commit()
		#self.conn.close()
	
	def run(self,cmd):
		# cmd="SELECT * FROM feedback;"
		mycur=self.conn.cursor()
		mycur.execute(cmd)
		table=(mycur.fetchall())
		return table
		
	def close(self):
		#self.conn.commit()
		self.conn.close()
		
	


# obj=DataBase()
# print(obj.run("select * from feedback"))
# obj.close()


