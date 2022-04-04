import json
import re
import csv
import time

target_labur = ["ERL", "ABS", "DEK", "ABL", "GRA", "ERG", "DAT", "INE", "SOZ", "GEN", "ALA", "GEL", "BNK", "DESK", "PAR", "INS", "ABU", "PRO", "DES", "ABZ", "AMM", "MOT"]
# aurrepos = ["ERL", "PRT", "AUR"]
# kategoriak = {}
# laburbalioak = {"AUR":{},"ERL":{},"PRT":{}}

with open('D:/Ahotsak/ETC/2022-morfeus-labur-balioak.json', 'r', encoding="utf-8") as jsonfile:
	morfeusfile = json.load(jsonfile)
	target = {}
	for laburdura in morfeusfile:
		if laburdura not in target_labur:
			continue
		target[laburdura] = {}
		for zati in morfeusfile[laburdura]:
			target[laburdura][zati] = laburdura

with open('D:/Ahotsak/ETC/2022-morfeus-labur-balioak-transformed.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(target, jsonfile, indent=2)
