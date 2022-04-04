import json
import re
import csv
import time

extrapos = ["ADB", "ADL", "ADT", "IZE", "ADJ", "ADI"]
aurrepos = ["ERL", "PRT", "AUR"]
kategoriak = {}
laburbalioak = {"AUR":{},"ERL":{},"PRT":{}}

with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_enriched.json', 'r', encoding="utf-8") as jsonfile:
	morfeusfile = json.load(jsonfile)

	for entry in morfeusfile:
		for analisia in entry['analisiak']:
			#print(str(analisia))
			zatiketa = analisia['zatiketa'].split(" + ")
			laburdurak = analisia['analisia'].split(" + ")
			#lema = zatiketa[0]
			pos = laburdurak[0]
			index = 1
			if len(laburdurak) > 1 and pos in aurrepos:
				if "^"+zatiketa[0] not in laburbalioak[pos]:
					laburbalioak[pos]["^"+zatiketa[0]] = 0
				laburbalioak[pos]["^"+zatiketa[0]] += 1
				if len(laburdurak) > 1:
					pos = laburdurak[1]
					index = 2

			while index < len(laburdurak):
				zati = zatiketa[index]
				laburdura = laburdurak[index]
				index += 1
				if laburdura in extrapos:
					pos += "+"+laburdura
					print('Found extrapos: '+pos, str(zatiketa), str(laburdurak))
					continue
				if laburdura not in laburbalioak:
					laburbalioak[laburdura] = {}
				if zati not in laburbalioak[laburdura]:
					laburbalioak[laburdura][zati] = 1
				else:
					laburbalioak[laburdura][zati] += 1

			if pos not in kategoriak:
				kategoriak[pos] = set()
			kategoriak[pos].add(analisia['lema'])

for pos in kategoriak:
	kategoriak[pos] = list(kategoriak[pos])


with open('D:/Ahotsak/ETC/2022-morfeus-labur-balioak.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(laburbalioak, jsonfile, indent=2)
with open('D:/Ahotsak/ETC/2022-morfeus-pos.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(kategoriak, jsonfile, indent=2)

# with open('D:/Ahotsak/ETC/2022-ETC-formak_MORFEUS_missinglemmata.txt', 'w', encoding="utf-8") as txtfile:
# 	txtfile.write("\n".join(list(missinglemmata)))
