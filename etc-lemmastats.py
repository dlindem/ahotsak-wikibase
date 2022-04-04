import json

with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak.json', 'r', encoding="utf-8") as jsonfile:
	etc = json.load(jsonfile)

longest_form = ''
for entry in etc:
	lemmalen = len(entry['lema'])
	for form in entry['formak']:
		if len(form['forma']) - lemmalen > len(longest_form):
			longest_form = form['forma']
			print(form['forma'])
print(longest_form)
