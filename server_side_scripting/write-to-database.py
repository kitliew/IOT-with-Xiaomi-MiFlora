#!/usr/bin/env python3

"""Remember to change MySQLdb user and passwd """

import cgi
import cgitb
import MySQLdb
from time import strftime


#CGI
cgitb.enable()

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from client
#localhost/write-to-database.py?temp=int
temp = str(form.getvalue("temp"))


#Display webpage
print("Content-type:text/html\n")

print("<title>Data Storage</title>")
print("<h1>Write-to-database</h1>")

#check if temp & value is in url
if "temp" not in form:
	print("Temp not found. Waiting for temperature input")
else:
	print("<h1>Temp found!</h1>")
	temperature = float(temp)
	print("<b1>Temp input is: {}</b1>".format(temperature))




#Database MySQL
db = MySQLdb.connect(host="localhost", user="usr", passwd="pass", db="templog")

cur = db.cursor()



while True:
	dateWrite = strftime("%Y-%m-%d")
	timeWrite = strftime("%H:%M:%S")
	sql = ('''INSERT INTO tempatinterrupt (Date, Time, Temperature) 
		VALUES ("{}","{}","{}")'''.format(dateWrite,timeWrite,temperature))
	print(sql)
	try:
		cur.execute(sql)
		db.commit()
		print("Process finish")
	except:
		db.rollback()
		print("Process Failed to Complete")
	cur.close()
	db.close()
	break
