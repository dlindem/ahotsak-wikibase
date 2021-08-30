import config
#import awb
import csv
import json
import requests

with open('D:/Ahotsak/herriak/wd_herriak.csv', 'r', encoding="utf-8") as csvfile:
	places = csv.DictReader(csvfile)
	placelinks = ""
	for place in places:
		#print(str(lang))

		qid = place['herria']
		name = place['label']
		print('Now getting html for placename: '+name)
		htmlfile = 'D:/Ahotsak/herriak/html/'+qid+'_'+name+'.html'
		html = requests.get('https://ahotsak.eus/'+name).text
		if '<body class="404error">' in html:
			print('Link did not work.')
			placelinks += qid+','+name+",None\n"
		elif '<body class="herria">' in html:
			print('Found place!')
			placelinks += qid+','+name+','+htmlfile+"\n"
			with open(htmlfile, 'w', encoding="utf-8") as file:
				file.write(html)
		print('Place done: '+name)
with open('D:/Ahotsak/herriak/herriak_htmlak.csv', 'w', encoding="utf-8") as outfile:
	outfile.write(placelinks)
