import sparql
import sys
import os
#sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import json

query = config.sparql_prefixes+"""
select (strafter(str(?awburl),"http://datuak.ahotsak.eus/entity/") as ?awbid) ?wdid

where { ?awburl adp:P1 ?wdid. }"""

print(query)

url = "https://datuak.ahotsak.eus/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot list of items from LexBib SPARQL.')

#go through sparqlresults

rowindex = 0
with open(config.datafolder+"wikibase/mappings/wdmappings.jsonl", "w", encoding="utf-8") as outfile:
	for row in sparqlresults:
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		linejson = {"awbid":item[0],"wdid":item[1]}
		outfile.write(json.dumps(linejson)+'\n')
print('Finished.')
