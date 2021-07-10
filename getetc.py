import csv
import requests
import config

with open(config.datafolder+'wikibase/mappings/lid_lemma.csv', 'r', encoding="utf-8") as mappingfile:
	lid_lem_csv = csv.DictReader(mappingfile)
	lid_lem = {}
	for row in lid_lem_csv:
		lid_lem[row['lemma']] = row['lid'].replace("http://datuak.ahotsak.eus/entity/","")

rowindex = 1
for lemma in lid_lem:
	print('Now getting html for lemma: '+lemma)
	htmlfile = 'D:/Ahotsak/ETC/'+lid_lem[lemma]+'_'+lemma+'.html'
	html = requests.get('https://www.ehu.eus/etc/?bila='+lemma).text
	with open(htmlfile, 'w', encoding="utf-8") as file:
		file.write(html)
	print('Lemma '+str(rowindex)+' done: '+lemma)
	rowindex +=1
