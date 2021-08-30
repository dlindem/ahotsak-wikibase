import csv
import awb

emapping = {
"ekialdeko-nafarra": "Q752",
"erronkarikoa": "Q753",
"zaraitzukoa": "Q754",
"erdialdekoa-gipuzkera": "Q755",
"erdigunekoa-g": "Q756",
"beterrikoa": "Q757",
"tolosaldekoa": "Q758",
"sartaldekoa-g": "Q759",
"goierrikoa": "Q760",
"urolaldekoa": "Q761",
"sortaldekoa-g": "Q762",
"bidasokoa": "Q763",
"basaburukoa": "Q764",
"imozkoa": "Q765",
"larraungoa": "Q766",
"leitzaldekoa": "Q767",
"mendebalekoa-bizkaiera": "Q768",
"sartaldekoa-m": "Q769",
"arratiakoa": "Q770",
"laudiokoa": "Q771",
"mungialdekoa": "Q772",
"nerbioi-ibarrekoa": "Q773",
"orozkokoa": "Q774",
"txorierrikoa": "Q775",
"uribe-kostakoa": "Q776",
"sortaldekoa-m": "Q777",
"debabarrenekoa": "Q778",
"debaerdikoa": "Q779",
"debagoienekoa": "Q780",
"durangaldekoa": "Q781",
"lea-artibaikoa": "Q782",
"tartekoa-m": "Q783",
"busturialdekoa": "Q784",
"otxandio-ingurukoa": "Q785",
"nafar-lapurtarra": "Q786",
"erdigunekoa-nl": "Q787",
"baigorrikoa": "Q788",
"uztaritze-ingurukoa": "Q789",
"sartaldekoa-nl": "Q790",
"kostatarra": "Q791",
"sara-ainhoa-ingurukoa": "Q792",
"sortaldekoa-nl": "Q793",
"amikuzekoa": "Q794",
"arberoakoa": "Q795",
"beskoitzekoa": "Q796",
"garazikoa": "Q797",
"nafarra": "Q798",
"baztangoa": "Q799",
"erdigunekoa-n": "Q800",
"arakilgoa": "Q801",
"lantzekoa": "Q802",
"ultzamakoa": "Q803",
"hego-sartaldekoa": "Q804",
"burundakoa": "Q805",
"sakanakoa": "Q806",
"hegoaldeko-nafarra": "Q807",
"ipar-sartaldekoa": "Q808",
"bortzirietakoa": "Q809",
"malerrekakoa": "Q810",
"sortaldekoa-n": "Q811",
"aezkoakoa": "Q812",
"erroibarkoa": "Q813",
"esteribarkoa": "Q814",
"zuberotarra": "Q815",
"basaburua": "Q816",
"pettarrakoa": "Q817"}

with open('D:/Ahotsak/euskalkiak/euskalki_hyps.csv', 'r', encoding="utf-8") as csvfile:
	hyps = csv.DictReader(csvfile)

	for hyp in hyps:
		qid = hyp['qid']
		if 'hyp2' in hyp and hyp['hyp2'] != "":
			hypernymqid = emapping[hyp['hyp2']]
			if hypernymqid != qid:
				statement = awb.updateclaim(qid,"P4", hypernymqid, "item")
		else:
			if 'hyp1' in hyp and hyp['hyp1'] != "":
				hypernymqid = emapping[hyp['hyp1']]
				if hypernymqid != qid:
					statement = awb.updateclaim(qid,"P4",emapping[hyp['hyp1']], "item")
			else:
				statement = awb.updateclaim(qid,"P4","Q819", "item")
