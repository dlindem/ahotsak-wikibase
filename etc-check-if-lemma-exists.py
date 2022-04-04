import json
import re
import csv

with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_enriched.json', 'r', encoding="utf-8") as jsonfile:
	etc = json.load(jsonfile)
with open('D:/Ahotsak/wikibase/mappings/lemma_lid.csv', 'r', encoding="utf-8") as csvfile:
	csvrows = csv.DictReader(csvfile)
	lemmalist = {}
	for row in csvrows:
		lemmalist[row['lemma']] = row['lexeme'].replace("http://datuak.ahotsak.eus/entity/","")

missinglemmata = set([])
for entry in etc:
	for analisia in entry['analisiak']:
		if analisia['lema'] not in lemmalist:
			#print('Missing lemma: '+analisia['lema'])
			missinglemmata.add(analisia['lema'])


# 	enrichedentry = {'forma': entry['forma'], 'analisiak':[]}
# 	if len(entry['analisiak']) == 0:
# 		emptyentries.append(entry)
#
# 		lema = re.search(r'^([^ ]+)', analisia['zatiketa']).group(1)
# 		#print('Found lemma '+lema+' in '+analisia['zatiketa']+'...')
# 		enrichedanalisia = analisia
# 		enrichedanalisia['lema'] = lema
# 		enrichedentry['analisiak'].append(enrichedanalisia)
#
# 	enrichedentries.append(enrichedentry)
#
# with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_enriched.json', 'w', encoding="utf-8") as jsonfile:
# 	json.dump(enrichedentries, jsonfile, indent=2)
with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_missinglemmata.txt', 'w', encoding="utf-8") as txtfile:
	txtfile.write("\n".join(list(missinglemmata)))
