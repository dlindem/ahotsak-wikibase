import csv
import sys
import os
#sys.path.insert(1, os.path.realpath(os.path.pardir))
import awb
import config


with open('D:/Ahotsak/herriak/del.csv', 'r', encoding="utf-8") as csvfile:
	dellist = csv.DictReader(csvfile)

	count = 0
	for row in dellist:
		count +=1
		print('\n['+str(count)+']: ')
		awb.removeclaim(row['del'])
