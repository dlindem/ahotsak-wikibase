import csv
import sys
import time
import re
import config
import json
import awb
import sparql

lidlist = [{"wdlid":"L50565","awblid":"L1"}]

for lidpair in lidlist:
	print('Now processing lidpair '+str(lidpair))

	existingforms = {}
	request = awb.site.get('wbgetentities', ids=lidpair['awblid'])
	if "success" in request:
		try:
			for form in request['entities'][lidpair['awblid']]['forms']:
				existingforms[form['representations']['eu']['value']] = {form['id']:form['grammaticalFeatures']}
		except Exception as ex:
			print('Get existing forms operation yields error:',str(ex))

	query = """
	select ?lemma ?order ?form ?wrep
	(concat('["',group_concat(strafter(str(?gram),"http://www.wikidata.org/entity/");SEPARATOR='","'),'"]') as ?gramgroup)
	 #(CONCAT('[ ',GROUP_CONCAT(?authordata; separator=","),' ]') AS ?authorsJson)
	where {wd:"""+lidpair['wdlid']+""" wikibase:lemma ?lemma;
	 ontolex:lexicalForm ?form .
	  ?form ontolex:representation ?wrep ;
	  wikibase:grammaticalFeature ?gram .
	  BIND(strafter(str(?form),"-F") as ?order)
	} group by ?lemma ?order ?form ?wrep ?gramgroup order by xsd:integer(?order)
	"""
	#print(query)
	print("Waiting for SPARQL forms retrieval...")
	sparqlresults = sparql.query("https://query.wikidata.org/sparql",query)
	#go through sparqlresults
	rowindex = 0
	for row in sparqlresults:
		done = False
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
		wd_form_id = item[2].replace("http://www.wikidata.org/entity/","")
		wrep = item[3]
		wd_gramgroup = json.loads(item[4])
		awb_gramgroup = []
		for wd_gram in wd_gramgroup:
			awb_gramgroup.append(awb.getqid(["Q20"],wd_gram))
		if wrep in existingforms:
			print('This form already exists; will check disambiguation, wdid alignment, gramgroup and skip: '+wrep)
			for existing_awbform in existingforms[wrep]:
				if awb_gramgroup == existingforms[wrep][existing_awbform]:
					print('This gramgroup is already there, at '+existing_awbform)
					awb.updateclaim(existing_awbform,"P1",wd_form_id,"string")
					done = True
		if done == False:
			print('Seems that this form-gramgroup is not there, will create it.')
			awb.newform(lidpair['awblid'], wrep, gram=awb_gramgroup, wdform_id=wd_form_id)
