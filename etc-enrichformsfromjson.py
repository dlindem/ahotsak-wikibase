import json
import re

with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS.json', 'r', encoding="utf-8") as jsonfile:
	etc = json.load(jsonfile)

emptyentries = []
enrichedentries = []
for entry in etc:
	enrichedentry = {'forma': entry['forma'], 'analisiak':[]}
	if len(entry['analisiak']) == 0:
		emptyentries.append(entry)
	for analisia in entry['analisiak']:
		lema = re.search(r'^([^ ]+)', analisia['zatiketa']).group(1)
		#print('Found lemma '+lema+' in '+analisia['zatiketa']+'...')
		enrichedanalisia = analisia
		enrichedanalisia['lema'] = lema
		enrichedentry['analisiak'].append(enrichedanalisia)

	enrichedentries.append(enrichedentry)

with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_enriched.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(enrichedentries, jsonfile, indent=2)
with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_emptyentries.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(emptyentries, jsonfile, indent=2)
