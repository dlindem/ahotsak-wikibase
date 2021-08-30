import config
import awb
import csv
import json
import requests

with open('D:/Ahotsak/herriak/herriak_htmlak.csv', 'r', encoding="utf-8") as csvfile:
	places = csv.DictReader(csvfile)
	placelinks = ""
	for place in places:
		#print(str(lang))

		qid = place['qid']
		name = place['izena']
		html = place['html']

		if html != "None":
			awb.stringclaim(qid,"P17",name.lower())
