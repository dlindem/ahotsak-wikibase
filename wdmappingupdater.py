import csv
import sys
import time
import re
import config
import json
import awb
import sparql

query = config.sparql_prefixes+"""
select * where {
?item adp:P1 ?wdid .
}
"""
#print(query)
print("Waiting for SPARQL ...")
sparqlresults = sparql.query("https://datuak.ahotsak.eus/query/sparql",query)
#go through sparqlresults
rowindex = 0
for row in sparqlresults:
	#time.sleep(0.5)
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
	awbid = item[0].replace("http://datuak.ahotsak.eus/entity/","")
	wdid = item[1]
	if awbid in awb.wdmappings:
		if awb.wdmappings[awbid] == wdid:
			print('Found known mapping',awbid,wdid)
		else:
			print('***Fatal error',awbid,'two mappings to wd:',wdid,awb.wdmappings[awbid])
	else:
		print('Found new mapping',awbid,wdid)
		awb.save_wdmapping(wdid, awbid)
