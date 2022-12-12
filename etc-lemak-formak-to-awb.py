import json
import re
import csv
import time
import sparql
import awb

#target_labur = ["ERL", "ABS", "DEK", "ABL", "GRA", "ERG", "DAT", "INE", "SOZ", "GEN", "ALA", "GEL", "BNK", "DESK", "PAR", "INS", "ABU", "PRO", "DES", "ABZ", "AMM", "MOT"]
# aurrepos = ["ERL", "PRT", "AUR"]
# kategoriak = {}
# laburbalioak = {"AUR":{},"ERL":{},"PRT":{}}
posqid = {
"ADI":"Q8",
"IZE":"Q7",
"ADJ":"Q11",
"ADB":"Q14"
}

allowed_aurrizkiak = [
"bait_ERL",
"ba_ERL"
]

allowed_morfeus_pos = {
"ADJARR":"Q11",
"IZEARR":"Q7",
"ADISIN":"Q8",
"ADBARR":"Q14"
}


print('\nLoading data...')
with open('D:/Ahotsak/ETC/writeprogress.txt', 'r', encoding="utf-8") as file:
	entrycount = int(file.read())
	print('\n'+str(entrycount)+' entries have been done in previous runs.')
	time.sleep(1)
with open('2022-morfeus-labur-balioak-transformed-glossed.json', 'r', encoding="utf-8") as jsonfile:
	morfeusgloss = json.load(jsonfile)
with open('morfeus_qid.csv', 'r', encoding="utf-8") as csvfile:
	morfeus_csv = csv.DictReader(csvfile)
	morfeus_qid = {}
	for row in morfeus_csv:
		morfeus_qid[row['laburLabel']] = row['laburQid']
with open('D:/Ahotsak/wikibase/mappings/lemma_lid.csv', 'r', encoding="utf-8") as csvfile:
	lemma_lid_csv = csv.DictReader(csvfile)
	lemma_lid = {}
	for row in lemma_lid_csv:
		lemma_lid[row['lemma']] = row['lexeme'].replace("https://datuak.ahotsak.eus/entity/","")
with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak_MORFEUS_enriched.json', 'r', encoding="utf-8") as jsonfile:
	etcfile = json.load(jsonfile)
	print('Data loaded.\n')

	loopcount = 0
	for entry in etcfile:
		loopcount += 1
		if loopcount <= entrycount:
			print('Entry done before, skipped.')
			continue

		entrycount += 1
		if entry['lema'] in lemma_lid:
			lid = lemma_lid[entry['lema']]
			print('Took known lid '+lid+' for lemma: '+entry['lema'])
		else:
			print('Lemma not found on awb, skipped: '+entry['lema'])
			continue
			lid = awb.newlexeme(entry['lema'],"eu","Q18")
			print('Created '+lid+' for lemma: '+entry['lema'])
		# set etc statement
		etcstatement = awb.updateclaim(lid,"P12",entry['lema'],"string")
		# set etc pos (lema)
		for pos in entry['kategoriak']:
			if pos in posqid:
				awb.setqualifier(lid,"P12",etcstatement,"P6",posqid[pos],"item")
			else:
				print('Found strange pos: '+pos+'... Will save to extrafile.')
				with open('D:/Ahotsak/ETC/2022-ETC-lemak-strangepos', 'a', encoding="utf-8") as jsonlfile:
					jsonlfile.write(json.dumps({'pos':pos,'entry':entry})+"\n")
		# set etc agerraldiak (lema)
		awb.setqualifier(lid, "P12", etcstatement, "P14", str(entry['lema_agerpenak']), "string")

		# get existing forms
		query = """
		PREFIX awb: <https://datuak.ahotsak.eus/entity/>
		PREFIX adp: <https://datuak.ahotsak.eus/prop/direct/>
		PREFIX ap: <https://datuak.ahotsak.eus/prop/>
		PREFIX aps: <https://datuak.ahotsak.eus/prop/statement/>
		PREFIX apq: <https://datuak.ahotsak.eus/prop/qualifier/>

		select distinct ?wrep (concat('["',group_concat(distinct strafter(str(?form),"https://datuak.ahotsak.eus/entity/");SEPARATOR='","'),'"]') as ?forms)
			(concat('["',group_concat(strafter(str(?gram),"https://datuak.ahotsak.eus/entity/");SEPARATOR='","'),'"]') as ?gramgroups)

			where {
		      awb:"""+lid+""" wikibase:lemma ?lemma;
			 ontolex:lexicalForm ?form .
			  ?form ontolex:representation ?wrep .
		 optional {	?form  wikibase:grammaticalFeature ?gram .}

		 } group by ?wrep ?forms ?gramgroups"""

		print("Waiting for SPARQL to deliver existing forms...")
		sparqlresults = sparql.query("https://datuak.ahotsak.eus/query/sparql",query)
	 	#go through sparqlresults
		existing_forms = {}
		for row in sparqlresults:
	 		#time.sleep(0.5)
			item = sparql.unpack_row(row, convert=None, convert_type={})
			existing_forms[item[0]] = json.loads(item[1])
		print('Found '+str(len(existing_forms))+' existing written representations.')
			#if len(item[2]) > 1: # existing gramgroups




		for form in entry['formak']:
			print('\nProcessing form: '+form['forma']+'\n')
			# process analisiak
			seen_analisiak = {}
			seen_grmgrp = {}
			for analisia in form['analisiak']:
				gramgrp = []
				zatiketa = analisia['zatiketa'].split(' + ')
				print(str(zatiketa))
				laburdurak = analisia['analisia'].split(' + ')
				print(str(laburdurak))
				if 'ATZ' in laburdurak: # TBD!!
					print('Form with ATZizki skipped and saved in atzizkidunak.csv')
					with open('D:/Ahotsak/ETC/atzizkidunak.csv', 'a') as atzfile:
						atzfile.write(lid+'\t'+form['forma']+'\t'+'+'.join(zatiketa)+'\t'+'+'.join(laburdurak)+'\n')
						continue
				glossed_laburdurak = []
				# remove Null-morphemes from analysis
				index = 0
				while index < len(zatiketa):
					if zatiketa[index] == "0":
						if index == 1 and len(zatiketa) == 2 and laburdurak[index] == "ABS":
							print('Found Null-morpheme ABS as only analysis. Left it in its place.')
							break
						else:
							del zatiketa[index]
							print('Removed Null analisis of type '+laburdurak[index]+'.')
							del laburdurak[index]
							#index += 1
					else:
						index += 1

				# process aurrizkiak
				if laburdurak[0] == "ERL" or laburdurak[0] == "PRT" or laburdurak[0] == "AUR":
					if laburdura[0] in allowed_aurrizkiak:
						aurrlabur = laburdurak.pop()
						aurrzati = zatiketa.pop()
						aurqid = morfeus_qid[morfeusgloss[aurrlabur][aurzati]]
						gramgrp.append(aurqid)
						print('Appended aurrizki to gramgrp: '+aurqid)
				# check POS and strip off
				pos = laburdurak.pop(0)
				zati1 = zatiketa.pop(0)

				seen_analisia = "+".join(laburdurak)
				if seen_analisia == "":
					seen_analisia = "NULL"
				if seen_analisia in seen_analisiak:
					if pos in seen_analisiak[seen_analisia]:
						print('This analysis has been processed for the same POS (duplicate after Null-analysis removal): '+seen_analisia+'.')
						continue
					else: # same analysis, new pos
						# write pos to form
						if pos in allowed_morfeus_pos:
							awb.setqualifier(formid, "P13", etcformstatement, "P6", allowed_morfeus_pos[pos], "item")
							seen_analisiak[seen_analisia].append(pos)
				else:
					seen_analisiak[seen_analisia] = [pos]

				if pos in posqid.keys() or (len(laburdurak) > 0 and laburdurak[0] in posqid.keys()): # means after the lemma comes a second lemma (stuff like "antropomorfizatu")
					print('Found one of these strange double-lempos items. Skipped: '+pos+'+'+str(laburdurak[0]),zati1+str(zatiketa[0]))
					time.sleep(1)
					continue
				if pos not in allowed_morfeus_pos:
					print('Found illegal value as morfeus lempos, will skip item: '+pos,'('+zati1+')')
					continue
					time.sleep(1)
				# go through atzizki analyisis
				for index in range(len(laburdurak)):
					gramqid = morfeus_qid[morfeusgloss[laburdurak[index]][zatiketa[index]]]
					labur_gloss = morfeusgloss[laburdurak[index]][zatiketa[index]]
					gramgrp.append(gramqid)
					glossed_laburdurak.append(labur_gloss)
				print('Defined gramgroup: '+str(gramgrp))
				if len(gramgrp) < 1:
					print('Empty gramgrp, analysis skipped.')
					continue
				if "+".join(gramgrp) not in seen_grmgrp:
					seen_grmgrp["+".join(gramgrp)] = [pos]
				else:
					print('An equal gramgrp has been written to this form already. Form ID stays the same.')
					seen_grmgrp["+".join(gramgrp)].append(pos)
					morfposstatement = awb.updateclaim(formid, "P24", allowed_morfeus_pos[pos], "item")
					print('*** Second POS has been added to this form-gramgroup.')
					continue
				# get form id for this analysis
				if form['forma'] in existing_forms and len(existing_forms[form['forma']]) > 0:
					formid = existing_forms[form['forma']].pop(0)
					print('Found existing matching written rep of form '+formid+' for form: '+form['forma'])
					update = awb.updateform(formid, form['forma'], gram=gramgrp)
				else:
					print('No matching written rep exists... Will create new form.')
					formid = awb.newform(lid, form['forma'], gram=gramgrp)
					# existing_forms[form['forma']].append(formid)
				# write ETC info
				etcformstatement = awb.updateclaim(formid, "P13", form["forma"], "string")
				awb.setqualifier(formid, "P13", etcformstatement, "P14", str(form['agerpenak']), "string")
				# write pos to form
				# awb.setqualifier(formid, "P13", etcformstatement, "P6", allowed_morfeus_pos[pos], "item")
				morfposstatement = awb.updateclaim(formid, "P24", allowed_morfeus_pos[pos], "item")
				# # write morphological analysis to P21 quali string
				# awb.setqualifier(formid, "P13", etcformstatement, "P21", "+".join(glossed_laburdurak), "string")

				# write MORFEUS info
				gramord = 0
				for gramqid in gramgrp:
					print(gramqid)
					gramord += 1
					morfstatement = awb.updateclaim(formid, "P22", gramqid, "item")
					awb.setqualifier(formid, "P21", morfstatement, "P23", str(gramord), "string")

		print('Finished processing '+lid+'.\n\n')

		with open('D:/Ahotsak/ETC/writeprogress.txt', 'w', encoding="utf-8") as file:
			file.write(str(entrycount))
	# end of entry loop

print('Finished.')
