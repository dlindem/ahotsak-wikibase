import json

with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak.json', 'r', encoding="utf-8") as jsonfile:
	etc = json.load(jsonfile)

formak = []
for entry in etc:
	for forma in entry['formak']:
		formajson = {'forma': forma['forma'].rstrip(), 'analisiak':[]}
		formak.append(formajson)

with open('D:/Ahotsak/ETC/2022-ETC-formak.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(formak, jsonfile, indent=2)
