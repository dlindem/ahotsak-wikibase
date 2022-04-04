import json
import re
import csv
import time

#target_labur = ["ERL", "ABS", "DEK", "ABL", "GRA", "ERG", "DAT", "INE", "SOZ", "GEN", "ALA", "GEL", "BNK", "DESK", "PAR", "INS", "ABU", "PRO", "DES", "ABZ", "AMM", "MOT"]
# aurrepos = ["ERL", "PRT", "AUR"]
# kategoriak = {}
# laburbalioak = {"AUR":{},"ERL":{},"PRT":{}}

with open('D:/Ahotsak/ETC/2022-morfeus-labur-balioak-transformed-glossed.json', 'r', encoding="utf-8") as jsonfile:
	morfeusfile = json.load(jsonfile)
	target = {}
	for laburdura in morfeusfile:
		for zati in morfeusfile[laburdura].keys():
			if morfeusfile[laburdura][zati] not in target:
				target[morfeusfile[laburdura][zati]] = {'Qid':'','morphemes':[]}
			target[morfeusfile[laburdura][zati]]['morphemes'].append(zati)


with open('D:/Ahotsak/ETC/2022-morfeus-labur-gloss-list.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(target, jsonfile, indent=2)
