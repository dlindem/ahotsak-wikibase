import json
import re
import csv
import time

with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak.json', 'r', encoding="utf-8") as jsonfile:
	etc = json.load(jsonfile)
with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_enriched.json', 'r', encoding="utf-8") as jsonfile:
	morfeusfile = json.load(jsonfile)
	morfeus = {}
	for entry in morfeusfile:
		morfeus[entry['forma']] = entry['analisiak']
	#print(str(morfeus['hankadun']))
# with open('D:/Ahotsak/wikibase/mappings/lemma_lid.csv', 'r', encoding="utf-8") as csvfile:
# 	csvrows = csv.DictReader(csvfile)
# 	lemmalist = {}
# 	for row in csvrows:
# 		lemmalist[row['lemma']] = row['lexeme'].replace("http://datuak.ahotsak.eus/entity/","")

targetlist = []
atzizkidunak = {}
aurrizkidunak = {}
for entry in etc:
	#print(str(entry))
	lema = entry['lema'].rstrip()

	print('Now processing lemma: '+lema)
	target = {'lema':lema, 'lema_agerpenak':entry['lema_agerpenak'], 'kategoriak':entry['kategoriak'], 'formak':[]}
	#print(str(entry['formak']))
	for etcform in entry['formak']:
		form = etcform['forma'].rstrip()
		#print('Now processing form: '+form)
		targetform = {'forma': form, 'agerpenak':etcform['agerpenak'],'analisiak':[]}
		if form in morfeus:
			#print('Found form '+form+' in MORFEUS.')
			#print(str(morfeus[form]))
			matchinglemma = []
			notmatchinglemma = []
			for analisia in morfeus[form]:
				if analisia['lema'] == lema:
					#print('* Found matching lemma: '+lema)
					matchinglemma.append(lema)
					if analisia['analisia'].startswith('AUR') or analisia['analisia'].startswith('ERL') or analisia['analisia'].startswith('PRT'):
						if form not in aurrizkidunak:
							aurrizkidunak[form] = []
						aurrizkidunak[form].append(analisia)
					elif " ATZ " in analisia['analisia']:
						if form not in atzizkidunak:
							atzizkidunak[form] = []
						atzizkidunak[form].append(analisia)
					else:
						targetform['analisiak'].append(analisia)
				else:
					notmatchinglemma.append(analisia['lema'])
			#for notmatching in notmatchinglemma:
				#print('** ETC lemma '+lema+', form '+form+': Found non-matching lemma: "'+notmatching+'". Matching lemmata for the same ETC lemma-form: '+str(matchinglemma))
		else:
			pass
			#print('!! Form '+form+' not found in MORFEUS')
		if len(targetform['analisiak']) > 0:
			target['formak'].append(targetform)

	# for analisia in entry['analisiak']:
	# 	if analisia['lema'] not in lemmalist:
	# 		#print('Will skip lemma not found in AWB: '+analisia['lema'])
	# 		continue
	# 	if (form.startswith(analisia['lema'])) == False:
	# 		print('Will skip morfeus lemma that is not contained in form: '+analisia['lema']+' ('+form+')')

	targetlist.append(target)
	#time.sleep(2)



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
with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak_MORFEUS_enriched.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(targetlist, jsonfile, indent=2)
with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak_MORFEUS_enriched_atzizkidunak.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(atzizkidunak, jsonfile, indent=2)
with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak_MORFEUS_enriched_aurrizkidunak.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(aurrizkidunak, jsonfile, indent=2)

# with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_missinglemmata.txt', 'w', encoding="utf-8") as txtfile:
# 	txtfile.write("\n".join(list(missinglemmata)))
