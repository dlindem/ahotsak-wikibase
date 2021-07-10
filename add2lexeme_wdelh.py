import csv
import config
import awb

infilename = config.datafolder+'wikidata/lid_lemma_category_AhId_Elhid_adverbs.csv'
#resourceitem = "Q19" #Q19: Elhuyar
#positem = "Q8" # Q7: substantibo, Q8: aditza

with open(infilename, encoding="utf-8") as csvfile:
	sourcedict = csv.DictReader(csvfile)

	for row in sourcedict:
		print('Now processing row: '+str(row))
		# existing_items = awb.searchlem(row['lemma'])
		# if len(existing_items) > 1:
		# 	print('*** Found two matching lemmata. That is strange.')
		# 	continue
		# if len(existing_items) == 1:
		# 	print('Found one matching lexeme: '+existing_items[0])
		# 	lexeme = existing_items[0].replace("http://datuak.filosarea.org/entity/","")
		# if len(existing_items) == 0:
		# 	print('No matching lemma for "'+row['lemma']+'", will create it.')
		if row['lemma'] in awb.lid_lem:
			lexeme = awb.lid_lem[row['lemma']]
			print('Found existing lemma to append data to: '+row['lemma']+ ' ('+lexeme+')')
		else:
			lexeme = awb.newlexeme(row['lemma'], "Q17", "Q18")
			awb.save_wdmapping(row["lexemeId"],lexeme)
		wdstatement = awb.updateclaim(lexeme, "P1", row["lexemeId"].replace("http://www.wikidata.org/entity/",""), "string")
		positem = awb.wdid2awbid(row["category"].replace("http://www.wikidata.org/entity/",""))
		quali = awb.setqualifier(lexeme, "P1", wdstatement, "P6", positem, "item")
		if row['ElhId'] != "":
			quali = awb.setqualifier(lexeme, "P1", wdstatement, "P7", row['ElhId'], "string")
