import json
import re
import csv
import time
import awb

#target_labur = ["ERL", "ABS", "DEK", "ABL", "GRA", "ERG", "DAT", "INE", "SOZ", "GEN", "ALA", "GEL", "BNK", "DESK", "PAR", "INS", "ABU", "PRO", "DES", "ABZ", "AMM", "MOT"]
# aurrepos = ["ERL", "PRT", "AUR"]
# kategoriak = {}
# laburbalioak = {"AUR":{},"ERL":{},"PRT":{}}

with open('D:/Ahotsak/ETC/2022-morfeus-labur-gloss-list.json', 'r', encoding="utf-8") as jsonfile:
	morfeusfile = json.load(jsonfile)

	for laburdura in morfeusfile:
		if morfeusfile[laburdura]['Qid'].startswith("Q"):
			Qid = morfeusfile[laburdura]['Qid']
		else:
			Qid = awb.newitemwithlabel("Q20", "eu", laburdura)
		morfeusfile[laburdura]['Qid'] = Qid
		for zati in morfeusfile[laburdura]['morphemes']:
			statement = awb.updateclaim(Qid, "P20", zati, "string")


with open('D:/Ahotsak/ETC/2022-morfeus-labur-gloss-list_Qids.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(target, jsonfile, indent=2)
