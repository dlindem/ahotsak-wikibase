import awb
import csv
import sys
import time
import re
import config
import json

infilename = config.datafolder+'ahotsak_taulak.json'

with open(infilename, encoding="utf-8") as jsonfile:
	sourcedict = json.load(jsonfile)

	for lemma in sourcedict:
		wdlid = sourcedict[lemma]['wdlid']
		print('\nNow processing lemma: '+lemma+', wikidata ['+wdlid+']')
		aholemid = awb.wdid2awbid(wdlid)
		#lexeme = awb.newlexeme(lemma, "Q2", "Q10")
		#print(lexeme)
		#wdstatement = awb.updateclaim(lexeme, "P4", row["lexemeId"], "url")
		#quali = awb.setqualifier(lexeme, "P4", wdstatement, "P57", "Q13", "item") # Q13: verb
		#ahostatement = awb.updateclaim(lexeme, "P55", resourceitem, "item")
		#quali = awb.setqualifier(lexeme, "P55", ahostatement, "P64", lemma, "string")

		if 'aldaerak' in sourcedict[lemma]:
			for aldaera in sourcedict[lemma]['aldaerak']:

				print('Now processing aldaera: '+aldaera)
				aldlex = awb.newlexeme(aldaera, "Q59", "Q18")
				classstatement = awb.updateclaim(aldlex, "P3", "Q750", "item") # honako hau da: Ahotsak Aldaera
				lemmastatement = awb.updateclaim(aldlex, "P9", lemma, "string")
				wdquali = awb.setqualifier(aldlex, "P9", lemmastatement, "P1", wdlid, "string")
				aholemstatement = awb.updateclaim(aldlex, "P10", aholemid, "lexeme")
				inversestatement = awb.updateclaim(aholemid, "P11", aldlex, "lexeme")

				for form in sourcedict[lemma]['aldaerak'][aldaera]:
					print('Now processing form: '+form+', will write to '+aldlex)
					createform = awb.newform(aldlex,form)
					print('Createform returned: '+str(createform))


print('\nFinished.')
