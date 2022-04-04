import config
import awb
import json

infilename = config.datafolder+'ahotsak_taulak.json'
with open(infilename, encoding="utf-8") as jsonfile:
	ahodict = json.load(jsonfile)

infilename = config.datafolder+'/ETC/formak.json'
with open(infilename, encoding="utf-8") as jsonfile:
	etcdict = json.load(jsonfile)

with open(config.datafolder+'/ETC/egindakoak.txt', 'r', encoding='utf-8') as donelistfile:
	donelist = donelistfile.read().split('\n')

for etclemma in etcdict:
	if etcdict[etclemma]['etc_agerraldiak'] > 0 and etclemma not in donelist and etclemma in ahodict and etclemma in awb.lid_lem:
		print('Will now process lemma: '+etclemma)
		etcstatement = awb.stringclaim(etcdict[etclemma]["aholid"], "P12", etclemma)
		agerstatement = awb.setqualifier(etcdict[etclemma]["aholid"], "P12", etcstatement, "P14", str(etcdict[etclemma]["etc_agerraldiak"]), "string")
		for etcform in etcdict[etclemma]['formak']:
			formid = awb.newform(etcdict[etclemma]["aholid"], etcform["forma"], gram=None, wdform_id=None)
			etcstatement = awb.stringclaim(formid, "P13", etcform["forma"])
			agerstatement = awb.setqualifier(formid, "P13", etcstatement, "P14", str(etcform["agerraldi"]), "string")
		with open(config.datafolder+'/ETC/egindakoak.txt', 'a', encoding='utf-8') as donelistfile:
			donelistfile.write(etclemma+'\n')
