import csv
import json
import awb
import config

infilename = config.datafolder+'wikidata/udalerriak.csv'
classitem = "Q63" #Q63: udalerri
#positem = "Q8" # Q7: substantibo, Q8: aditza

with open(infilename, encoding="utf-8") as csvfile:
	sourcedict = csv.DictReader(csvfile)

	for row in sourcedict:
		print('Now processing row: '+str(row))
		newqid = awb.newitemwithlabel([classitem], "eu", row['itemLabel'])
		wdstatement = awb.stringclaim(newqid,"P1",row['item'].replace('http://www.wikidata.org/entity/',''))
