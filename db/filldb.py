#! /usr/bin/python

import os
import sys
import mysqldb
import fileinput

if len(sys.argv) != 3:
	print """
	You should specify the file to import to datebase and the table 
	name in database.
	For example:
		./filldb.py m1305.txt m1305_day_k
	"""
	exit (0)

datafile = sys.argv[1]
sqltable = sys.argv[2]
print "To import the data from [ %s ] to database table [ %s ]" % (datafile, sqltable)
#exit (0)

db = mysqldb.MYSQL ('localhost', 'win', 'winfwinf', 'futures')
db.connect()

file = open(datafile)
#line = file.readline()
#print line.strip('\n')
#cmdStr = 'echo %s | awk \'BEGIN {FS=","} {OFS=","} END {print $1}\'' % line.strip()
#res = os.popen(cmdStr)
#values = '"' + res.read().strip() + '"'
#print values
#cmdStr = 'echo %s | awk \'BEGIN {FS=","} {OFS=","} END {print $2, $3, $4, $5, $6, $7, $8}\'' % line.strip()
#res = os.popen(cmdStr)
#values = values + ',' + res.read().strip()
#print values
#db.insert('m1305_day_k', values)

#lines = file.readlines(10000)
#for line in lines:
	#print line

for line in fileinput.input(datafile):
	cmdStr = 'echo %s | awk \'BEGIN {FS=","} {OFS=","} END {print $1}\'' % line.strip()
	res = os.popen(cmdStr)
	values = '"' + res.read().strip() + '"'
	cmdStr = 'echo %s | awk \'BEGIN {FS=","} {OFS=","} END {print $2, $3, $4, $5, $6, $7, $8}\'' % line.strip()
	res = os.popen(cmdStr)
	values = values + ',' + res.read().strip()
	print values
	db.insert(sqltable, values)
	
file.close()	
db.close()
