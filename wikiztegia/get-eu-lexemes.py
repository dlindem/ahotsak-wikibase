import requests, json

pagelist = []
cmcontinue = None
while cmcontinue != True:
	if (not cmcontinue):
		r = requests.get('https://eu.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Kategoria:Euskara&cmprop=title&format=json&cmlimit=500')
	else:
		r = requests.get('https://eu.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Kategoria:Euskara&cmprop=title&format=json&cmlimit=500&cmcontinue='+cmcontinue)
	print(r.json())
	for categorymember in r.json()['query']['categorymembers']:
		pagelist.append(categorymember['title'])
	if 'continue' in r.json():
		cmcontinue = r.json()['continue']['cmcontinue']
	else:
		cmcontinue = True # all batches downloaded

with open ('D:/Ahotsak/wikiztegia/wikt-eu-pages.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(pagelist, jsonfile, indent = 2)
