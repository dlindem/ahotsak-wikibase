import csv
import config
import awb

infilename = config.datafolder+'wikibase/tmp.txt'


with open(infilename, encoding="utf-8") as file:
	list = file.read().split('\n')
	for guid in list:
		print('Will delete statement '+guid)
		awb.removeclaim(guid)
