import csv
import config
import awb

infilename = config.datafolder+'wikidata/wdlid_ElhId.csv'
resourceitem = "Q19" #Q19: Elhuyar
#positem = "Q8" # Q7: substantibo, Q8: aditza

with open(infilename, encoding="utf-8") as csvfile:
	sourcedict = csv.DictReader(csvfile)
	lex_elh = {}
	for row in sourcedict:
		lex_elh[row['lexemeId'].replace("http://www.wikidata.org/entity/","")] = row['ElhId']

for awbid in awb.wdmappings:
	wdid = awb.wdmappings[awbid]
	if awbid.startswith('L') and wdid in lex_elh:
		wdstatement = awb.updateclaim(awbid, "P1", wdid, "string")
		quali = awb.setqualifier(awbid, "P1", wdstatement, "P7", lex_elh[wdid], "string")
