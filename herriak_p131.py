import config
import awb
import csv
import json
import requests

lurraldeak = [
"Q81801",
"Q638503",
"Q671023",
"Q4018",
"Q93366",
"Q95010",
"Q673040"
]


with open('D:/Ahotsak/herriak/herriak_p131.csv', 'r', encoding="utf-8") as csvfile:
	places = csv.DictReader(csvfile)

	for place in places:
		#print(str(lang))

		qid = place['herria'].replace("http://datuak.ahotsak.eus/entity/","")
		p131 = place['p131'].replace("http://www.wikidata.org/entity/","")

		if p131 in lurraldeak:
			p131_awb = awb.wdid2awbid(p131)
			statement = awb.updateclaim(qid, "P19", p131_awb, "item")
			print('Written: '+place['herriLabel']+' > '+place['p131Label'])
