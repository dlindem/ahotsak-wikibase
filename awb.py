import mwclient
import json
import urllib.parse
import time
import re
import csv
import requests
import sys
import unidecode
import logging
import sparql
from wikidataintegrator import wdi_core, wdi_login
import config

# Properties with constraint: max. 1 value
card1props = config.card1props

# Logging config
logging.basicConfig(filename=config.datafolder+'logs/awb.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

# # WDI setup
# mediawiki_api_url = "https://datuak.ahotsak.eus/w/api.php" # <- change to applicable wikibase
# sparql_endpoint_url = "https://datuak.ahotsak.eus/query/sparql"  # <- change to applicable wikibase
# login = wdi_login.WDLogin(config.awbuser, config.awbuserpass, mediawiki_api_url=mediawiki_api_url)
# awbEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

# ahotsak wikibase OAuth for mwclient
site = mwclient.Site('datuak.ahotsak.eus')
def get_token():
	global site
	login = site.login(username=config.awbuser, password=config.awbuserpass)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for datuak.ahotsak.eus.")
	return token
token = get_token()

def load_wdmappings():
	wdmappings = {}
	try:
		with open(config.datafolder+'wdmappings.jsonl', encoding="utf-8") as f:
			mappings = f.read().split('\n')
			count = 0
			for mapping in mappings:
				count += 1
				if mapping != "":
					try:
						mappingjson = json.loads(mapping)
						#print(mapping)
						wdmappings[mappingjson['awbid']] = mappingjson['wdid']
					except Exception as ex:
						print('Found unparsable mapping json in wdmappings.jsonl line ['+str(count)+']: '+mapping)
						print(str(ex))
						pass
	except Exception as ex:
		print ('Error: wdmappings file does not exist. Will start a new one.')
		print (str(ex))

	print('Known awb-WD item mappings loaded.')
	return wdmappings
wdmappings = load_wdmappings()

# Get equivalent awb item qidnum from wikidata Qid
def wdid2awbid(wdid):
	#print('Will try to find awbid for '+wdid+'...')
	global wdmappings
	for key, value in wdmappings.items():
		if wdid == value:
			print('Found awbid in wdids known mappings: '+key)
			return key

# Adds a new awbqid-wdqid mapping to wdmappings.jsonl mapping file
def save_wdmapping(wdid, awbid):
	with open(config.datafolder+'wdmappings.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps({'wdid':wdid.replace("http://www.wikidata.org/entity/",""),'awbid':awbid.replace("https://datuak.ahotsak.eus/entity/","")})+'\n')

# # search for lemma, return matching lid list
# def searchlem(lemma):
# 	lemma = '"'+lemma+'"'
#
#
# 	query = """
# 	PREFIX fs: <http://datuak.filosarea.org/entity/>
# 	PREFIX fdp: <http://datuak.filosarea.org/prop/direct/>
# 	PREFIX fp: <http://datuak.filosarea.org/prop/>
# 	PREFIX fps: <http://datuak.filosarea.org/prop/statement/>
# 	PREFIX fpq: <http://datuak.filosarea.org/prop/qualifier/>
#
# 	select ?l ?lemma ?lang #?lexcat
# 	 where {
#
# 	  ?l rdf:type ontolex:LexicalEntry .
# 	  ?l dct:language ?lang .
# 	  ?l wikibase:lemma ?lemma .
#
# 	  filter (str(?lemma) = """+lemma+""")
#
#
#
#
# 	}
# 	"""
#
# 	#print(query)
#
# 	url = "https://datuak.filosarea.org/query/sparql"
# 	while True:
# 		try:
# 			#print("Waiting for SPARQL...")
# 			sparqlresults = sparql.query(url,query)
# 			if sparqlresults:
# 				break
# 			#print('\nGot answer from FiloSarea SPARQL.')
# 		except Exception as ex:
# 			print('fs.searchlem sparql failed...will try again. Error: '+str(ex))
# 			time.sleep(5)
# 		time.sleep(5)
#
# 	#go through sparqlresults
# 	rowindex = 0
# 	lids = []
# 	for row in sparqlresults:
# 		rowindex += 1
# 		item = sparql.unpack_row(row, convert=None, convert_type={})
# 		#print('\nNow processing sparql result item ['+str(rowindex)+']:\n'+str(item))
# 		lid = item[0]
# 		lemma = item[1]
# 		#lexcat = item[3]
# 		lids.append(lid)
# 	return lids

# load and save lid_lemma mapping
with open(config.datafolder+'lid_lemma.csv', 'r', encoding="utf-8") as mappingfile:
	lid_lem_csv = csv.DictReader(mappingfile)
	lid_lem = {}
	for row in lid_lem_csv:
		lid_lem[row['lemma']] = row['lid'].replace("https://datuak.ahotsak.eus/entity/","")
def save_lidmapping(lid,lemma):
	with open(config.datafolder+'lid_lemma.csv', 'a', encoding="utf-8") as mappingfile:
		mappingfile.write(lid+","+lemma+"\n")

# search for lemma, return matching lid list
def searchlem(lemma):

	global lid_lem
	if lemma in lid_lem:
		return [lid_lem[lemma]]
	else:
		return []

	print('lemma not found in lid_lemma mapping, trying with SPARQL...')
	lemma = '"'+lemma+'"'
	query = """
	PREFIX awb: <https://datuak.ahotsak.eus/entity/>
	PREFIX adp: <https://datuak.ahotsak.eus/prop/direct/>
	PREFIX ap: <https://datuak.ahotsak.eus/prop/>
	PREFIX aps: <https://datuak.ahotsak.eus/prop/statement/>
	PREFIX apq: <https://datuak.ahotsak.eus/prop/qualifier/>

	select ?l ?lemma ?lang #?lexcat
	 where {

	  ?l rdf:type ontolex:LexicalEntry .
	  ?l dct:language ?lang .
	  ?l wikibase:lemma ?lemma .

	  filter (str(?lemma) = """+lemma+""")
	}
	"""

	#print(query)

	url = "https://datuak.ahotsak.eus/query/sparql"
	while True:
		try:
			#print("Waiting for SPARQL...")
			sparqlresults = sparql.query(url,query)
			if sparqlresults:
				break
			#print('\nGot answer from FiloSarea SPARQL.')
		except Exception as ex:
			print('awb.searchlem sparql failed...will try again. Error: '+str(ex))
			time.sleep(5)
		time.sleep(5)

	#go through sparqlresults
	rowindex = 0
	lids = []
	for row in sparqlresults:
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		#print('\nNow processing sparql result item ['+str(rowindex)+']:\n'+str(item))
		lid = item[0].replace("https://datuak.ahotsak.eus/entity/","")
		lemma = item[1]
		#lexcat = item[3]
		lids.append(lid)
	return lids


# Get equivalent awb item qidnum from wikidata Qid
def wdid2awbid(wdqid):
	print('Will try to find awbqid for '+wdqid+'...')
	global wdmappings
	# Try to find awbqid from known mappings
	for key, value in wdmappings.items():
		if wdqid == value:
			print('Found awbqid in wdmappings known mappings.')
			return key
	# Try to find awbqid via SPARQL
	url = "https://datuak.ahotsak.eus/query/sparql?format=json&query=PREFIX%20awb%3A%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fprop%2Fdirect%2F%3E%0A%0Aselect%20%3FawbItem%20where%0A%7B%20%3FawbItem%20ldp%3AP1%20wd%3A"+wdqid+"%20.%20%7D"

	while True:
		try:
			r = requests.get(url)
			awbqid = r.json()['results']['bindings'][0]['awbItem']['value'].replace("https://datuak.ahotsak.eus/entity/","")
			if len(r.json()['results']['bindings']) > 1:
				print('***WARNING: This wdid is found TWICE in awb: '+wdqid)
				logging.warning('This wdid is found TWICE in awb: '+wdqid)
		except Exception as ex:
			print('Error: SPARQL request returned no awbid.')
			time.sleep(2)
			return False
		break
	print('Found awbqid '+awbqid+' not in mappingfile, but via SPARQL, will add it to mappingfile.')
	save_wdmapping(wdqid, awbqid)
	return awbqid

# creates a new lexeme
def newlexeme(lemma, lang, pos):
	global token

	data = {"type":"lexeme","lemmas":{"eu":{"value":lemma,"language":"eu"}},"lexicalCategory":pos,"language":lang}
	done = False
	while (not done):
		try:
			itemcreation = site.post('wbeditentity', token=token, format="json", new="lexeme", bot=1, data=json.dumps(data))
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				time.sleep(4)
			continue
		#print(str(itemcreation))
		if itemcreation['success'] == 1:
			done = True
			lid = itemcreation['entity']['id']
			print('Lexeme creation '+lid+': success.')
		else:
			print('Lexeme creation failed, will try again...')
			time.sleep(2)
		save_lidmapping(lid,lemma)
		return lid

# creates a new form
def newform(lid, form, gram=None, wdform_id=None, nodupcheck = None):
	global token

	existingforms = {}
	request = site.get('wbgetentities', ids=lid)
	if "success" in request:
		try:
			for existform in request['entities'][lid]['forms']:
				existingforms[existform['representations']['eu']['value']] = existform['id']
			if nodupcheck and form in existingforms:
				print('This form already exists: '+existingforms[form])
				return existingforms[form]
		except Exception as ex:
			print('Get existing forms operation failed for: '+lid) #,str(ex))

	data = {"representations":{"eu":{"value":form,"language":"eu"}}}
	if gram:
		data["grammaticalFeatures"] = gram
	done = 0
	while done < 1:
		try:
			formcreation = site.post('wbladdform', token=token, format="json", lexemeId=lid, bot=1, data=json.dumps(data))
			#itemcreation = site.post('wbeditentity', token=token, format="json", id=lid, bot=1, data=json.dumps(data))
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				time.sleep(4)
				done += 0.2
			continue
		#print(str(itemcreation))
		if formcreation['success'] == 1:
			#print(str(formcreation))
			formid = formcreation['form']['id']
			print('Form creation for '+lid+': success: '+formid)
			if wdform_id:
				updateclaim(formid,"P1",wdform_id,"string")
			return formid
		else:
			print('Form creation failed, will try again...')
			time.sleep(2)
			done += 0.2
	print('awb.newform failed 5 times.'+lid+','+form+','+str(gram)+','+wdform_id)
	logging.error('awb.newform failed 5 times.'+lid+','+form+','+str(gram)+','+wdform_id)
	return False


# updates a form
def updateform(form_id, form, gram=None, wdform_id=None):
	global token
	if wdform_id:
		updateclaim(form_id,"P1",wdform_id,"string")
	data = {"representations":{"eu":{"value":form,"language":"eu"}}}
	if gram:
		data["grammaticalFeatures"] = gram
	done = 0
	while done < 1:
		try:
			formcreation = site.post('wbleditformelements', token=token, format="json", formId=form_id, bot=1, data=json.dumps(data))

		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				time.sleep(4)
				done += 0.2
			continue
		#print(str(itemcreation))
		if formcreation['success'] == 1:
			print('Form update for '+form_id+': success.')
			return form_id
		else:
			print('Form update for '+form_id+' failed, will try again...')
			time.sleep(2)
			done += 0.2
	print('awb.updateform failed 5 times.'+form_id+','+form+','+str(gram)+','+wdform_id)
	logging.error('awb.updateform failed 5 times.'+form_id+','+form+','+str(gram)+','+wdform_id)
	return False

#remove form
def removeform(form_id):
	global token
	done = 0
	while done < 1:
		try:
			formremoval = site.post('wblremoveform', token=token, format="json", id=form_id, bot=1)

		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				time.sleep(4)
				done += 0.2
			continue
		#print(str(itemcreation))
		if formremoval['success'] == 1:
			print('Form removal for '+form_id+': success.')
			return True
		else:
			print('Form removal for '+form_id+' failed, will try again...')
			time.sleep(2)
			done += 0.2
	print('awb.removeform failed 5 times.'+form_id)
	logging.error('awb.removeform failed 5 times.'+form_id)
	return False
# creates a new item
def newitemwithlabel(awbclasses, labellang, label, type="item"): # awbclasses: 'instance of' (P5)
	global token
	#global knownqid
	if isinstance(awbclasses, str) == True: # if a single value is passed as string, not as list
		awbclasses = [awbclasses]
	data = {"labels":{labellang:{"language":labellang,"value":label}}}
	done = False
	while (not done):
		try:
			itemcreation = site.post('wbeditentity', token=token, new=type, bot=1, data=json.dumps(data))
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				time.sleep(4)
			continue
		#print(str(itemcreation))
		if itemcreation['success'] == 1:
			done = True
			qid = itemcreation['entity']['id']
			print('Item creation for '+qid+': success.')
		else:
			print('Item creation failed, will try again...')
			time.sleep(2)

		for awbclass in awbclasses:
			if awbclass != None:
				done = False
				while (not done):
					claim = {"entity-type":type,"numeric-id":int(awbclass.replace("Q",""))}
					classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P3", snaktype="value", value=json.dumps(claim))
					try:
						if classclaim['success'] == 1:
							done = True
							print('Instance-of-claim creation for '+qid+': success. Type is '+type+'. Class is '+awbclass)
							#time.sleep(1)
					except:
						print('Claim creation failed, will try again...')
						time.sleep(2)
		return qid



# function for wikibase item creation (after check if it is known)
#token = get_token()
def getqid(awbclasses, wdItem, onlyknown=False): # awbclass: object of 'instance of' (P5), wdItem = wikidata-entity (P1) of the (known or new) q-item
	global token
	global wdmappings
	if isinstance(awbclasses, str) == True: # if a single value is passed as string, not as list
		awbclasses = [awbclasses]
	awbid = wdid2awbid(wdItem)
	if awbid != False:
		print(wdItem+' is a known wikibase item: Qid '+awbid+', no need to create it.')
		return awbid
	#if onlyknown:
		#print('This wd item is not in the known mapping: '+wdItem)
		#return False
	#wdItemSafe = urllib.parse.quote(wdItem, safe='~', encoding="utf-8")
	# url = "https://datuak.ahotsak.eus/query/sparql?format=json&query=SELECT%20%3FawbItem%20%0AWHERE%20%0A%7B%20%20%3FawbItem%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fprop%2Fdirect%2FP5%3E%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fentity%2F"+awbclasses[0]+"%3E.%20%0A%0A%20%20%20%3FawbItem%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fprop%2Fdirect%2FP4%1E%20%3C"+wdItem+"%3E%20.%0A%7D"
	# done = False
	# while (not done):
	# 	try:
	# 		r = requests.get(url)
	# 		results = r.json()['results']['bindings']
	# 	except Exception as ex:
	# 		print('Error: SPARQL request failed.')
	# 		time.sleep(2)
	# 		continue
	#
	# 	done = True
	#if len(results) == 0:
	else:
		print('Found no Qid for Wikidata Item '+wdItem+', will create it.')
		claim = {"claims":[{"mainsnak":{"snaktype":"value","property":"P1","datavalue":{"value":wdItem,"type":"string"}},"type":"statement","rank":"normal"}]}
		done = False
		while (not done):
			try:
				itemcreation = site.post('wbeditentity', token=token, new="item", bot=1, data=json.dumps(claim))
			except Exception as ex:
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					token = get_token()
				else:
					print(str(ex))
					time.sleep(4)
				continue
			#print(str(itemcreation))
			if itemcreation['success'] == 1:
				done = True
				qid = itemcreation['entity']['id']
				print('Item creation for wikidata '+wdItem+': success. QID = '+qid)
			else:
				print('Item creation failed, will try again...')
				time.sleep(2)
		wdmappings[wdItem] = qid
		save_wdmapping(wdItem,qid)


		for awbclass in awbclasses:
			done = False
			while (not done):
				claim = {"entity-type":"item","numeric-id":int(awbclass.replace("Q",""))}
				classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P3", snaktype="value", value=json.dumps(claim))
				try:
					if classclaim['success'] == 1:
						done = True
						print('Instance-of-claim creation for '+wdItem+': success. Class is '+awbclass)
						#time.sleep(1)
				except:
					print('Claim creation failed, will try again...')
					time.sleep(2)

		return qid
	# elif len(results) > 1:
	# 	print('*** Error: Found more than one awb item for one wd item that should be unique... will take the first result.')
	# 	qid = results[0]['awbItem']['value'].replace("https://datuak.ahotsak.eus/entity/","")
	# 	wdmappings[wdItem] = qid
	# 	save_wdmapping(wdItem,qid)
	# 	return qid
	# elif len(results) == 1:
	# 	qid = results[0]['awbItem']['value'].replace("https://datuak.ahotsak.eus/entity/","")
	# 	print('Found '+wdItem+' not in wdmappings file but on awb: Qid '+qid+'; no need to create it, will add to wdmappings file.')
	# 	wdmappings[wdItem] = qid
	# 	save_wdmapping(wdItem,qid)
	# 	return qid

#get label
def getlabel(qid, lang):
	done = False
	while True:
		request = site.get('wbgetentities', ids=qid, props="labels", languages=lang)
		if request['success'] == 1 and lang in request["entities"][qid]["labels"]:
			return request["entities"][qid]["labels"][lang]["value"]
		elif lang not in request["entities"][qid]["labels"]:
			print('No label for this language found on awb.')
			return None
		else:
			print('Something went wrong with label retrieval for '+qid+', will try again.')
			time.sleep(3)

#create item claim
def itemclaim(s, p, o):
	global token

	done = False
	value = json.dumps({"entity-type":"item","numeric-id":int(o.replace("Q",""))})
	while (not done):
		try:
			request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=1)
			if request['success'] == 1:
				done = True
				claimId = request['claim']['id']
				print('Claim creation done: '+s+' ('+p+') '+o+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print('Claim creation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return claimId

#create string (or url) claim
def stringclaim(s, p, o):
	global token

	done = False
	value = '"'+o.replace('"', '\\"')+'"'
	while (not done):
		try:
			request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=1)
			if request['success'] == 1:
				done = True
				claimId = request['claim']['id']
				print('Claim creation done: '+s+' ('+p+') '+o+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print('Claim creation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return claimId

#create string (or url) claim
def setlabel(s, lang, val, type="label"):
	global token

	done = False
	count = 0
	value = val[0:399] # max. 400 chars
	while count < 5:
		count += 1
		try:
			if type == "label":
				request = site.post('wbsetlabel', id=s, language=lang, value=value, token=token, bot=1)
			elif type == "alias":
				request = site.post('wbsetaliases', id=s, language=lang, add=value, token=token, bot=1)
			if request['success'] == 1:
				print('Label creation done: '+s+' ('+lang+') '+val+', type: '+type)
				return True
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			elif 'Unrecognized value for parameter "language"' in str(ex):
				print('Cannot set label in this language: '+lang)
				logging.warning('Cannot set label in this language: '+lang)
				break
			else:
				print('Label set operation '+s+' ('+lang+') '+val+' failed, will try again...\n'+str(ex))
				logging.error('Label set operation '+s+' ('+lang+') '+val+' failed, will try again...', exc_info=True)
				time.sleep(4)
	# log.add
	print ('*** Label set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	logging.warning('Label set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	return False

#create string (or url) claim
def setdescription(s, lang, val):
	global token

	done = False
	count = 0
	value = val # insert operations if necessary
	while count < 5:
		count += 1
		try:
			request = site.post('wbsetdescription', id=s, language=lang, value=value, token=token, bot=1)
			if request['success'] == 1:
				print('Description creation done: '+s+' ('+lang+') "'+val+'".')
				return True
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			elif 'Unrecognized value for parameter "language"' in str(ex):
				print('Cannot set description in this language: '+lang)
				logging.warning('Cannot set description in this language: '+lang)
				break
			elif 'already has label' in str(ex) and 'using the same description text.' in str(ex):
				# this is a hot candidate for merging
				print('*** Oh, it seems that we have a hot candidate for merging here... Writing info to mergecandidates.log')
				with open ('logs/mergecandidates.log', 'a', encoding='utf-8') as mergecandfile:
					mergecand = re.search(r'\[\[Item:(Q\d+)',str(ex)).group(1)
					mergecandfile.write(s+' and '+mergecand+' : '+val+'\n')
				break
			else:
				print('Description set operation '+s+' ('+lang+') '+val+' failed, will try again...\n'+str(ex))
				logging.error('Description set operation '+s+' ('+lang+') '+val+' failed, will try again...', exc_info=True)
				time.sleep(4)
	# log.add
	print ('*** Description set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	logging.warning('Description set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	return False

#get claims from qid
def getclaims(s, p):

	done = False
	while (not done):
		#print('Getclaims:',s, p)
		try:
			if s.startswith("Q") or s.startswith("P"):
				#print("Getclaims for items triggered.")
				if p == True: # get all claims
					request = site.get('wbgetclaims', entity=s)
				else:
					request = site.get('wbgetclaims', entity=s, property=p)
				return (s, request['claims'])
			if s.startswith("L"):
				#print("Getclaims for lexeme triggered.")
				request = site.get('wbgetentities', ids=s)
				#print(str(request))
				if "entities" in request and s in request['entities'] and "claims" in request['entities'][s] and p in request['entities'][s]['claims']:
					#print('GetLexemeClaims will return: '+s, request['entities'][s]['claims'][p])
					return (s, request['entities'][s]['claims'])
				else:
					return (s, [])

		except Exception as ex:
			if 'unresolved-redirect' in str(ex):

				#get redirect target
				url = "https://datuak.ahotsak.eus/query/sparql?format=json&query=PREFIX%20awb%3A%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fprop%2awbtatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdatuak.ahotsak.eus%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%28strafter%28str%28%3Fredirect%29%2C%22http%3A%2F%2Fdatuak.ahotsak.eus%2Fentity%2F%22%29%20as%20%3Frqid%29%20where%0A%7Bawb%3AQ2874%20owl%3AsameAs%20%3Fredirect.%7D%0A%20%20%0A"
				subdone = False
				while (not subdone):
					try:
						r = requests.get(url)
						bindings = r.json()['results']['bindings']
					except Exception as ex:
						print('Error: SPARQL request for redirects failed: '+str(ex))
						time.sleep(2)
						continue
					subdone = True

				if 'rqid' in bindings[0]:
					print('Found redirect target '+bindings[0]['rqid']['value']+', will use that instead.')
					s = bindings[0]['rqid']['value']
					continue

			if 'no-such-entity' in str(ex):
				print(s+' does not exist.')
				logging.error(s+' does not exist (wbgetclaims error.)')
				return False

			print(str(ex))

			print('\nGetclaims operation failed, will try again...\n'+str(ex))
			time.sleep(4)
		print('Getclaims operation failed, will try again...\n')
		time.sleep(4)

#get claim from statement ID
def getclaimfromstatement(guid):
	done = False
	while (not done):
		try:
			request = site.get('wbgetclaims', claim=guid)

			if "claims" in request:
				done = True
				return request['claims']
		except Exception as ex:
			print('Getclaims operation failed, will try again...\n'+str(ex))
			time.sleep(4)

#update claims
def updateclaim(s, p, o, dtype): # for novalue: o="novalue", dtype="novalue"
	global card1props
	global token

	if dtype == "time":
		data=[(wdi_core.WDTime(o['time'], prop_nr=p, precision=o['precision']))]
		item = awbEngine(wd_item_id=s, data=data)
		print('Successful time object write operation: '+item.write(login))
		# TBD: duplicate statement control
		claims = getclaims(s,p)
		#print(str(claims))
		return claims[1][p][0]['id']
	elif dtype == "string" or dtype == "url" or dtype == "monolingualtext":
		value = '"'+o.replace('"', '\\"')+'"'
	elif dtype == "item" or dtype =="wikibase-entityid":
		value = json.dumps({"entity-type":"item","numeric-id":int(o.replace("Q",""))})
	elif dtype == "lexeme":
		print('Will try to write Lexeme as claimobject: '+o)
		value = json.dumps({"entity-type":"lexeme","id":o,"numeric-id":int(o.replace("L",""))})
	elif dtype == "novalue":
		value = "novalue"
	#print('Will go for claims for',s,p)
	claims = getclaims(s,p)
	if claims == False:
		return False
	s = claims[0]
	claims = claims[1]
	foundobjs = []
	if claims and bool(claims):
		statementcount = 0
		for claim in claims[p]:
			statementcount += 1
			guid = claim['id']
			#print(str(claim['mainsnak']))
			if claim['mainsnak']['snaktype'] == "value":
				foundo = claim['mainsnak']['datavalue']['value']
			elif claim['mainsnak']['snaktype'] == "novalue":
				foundo = "novalue"
			if isinstance(foundo, dict): # foundo is a dict in case of datatype wikibaseItem
				#print(str(foundo))
				foundo = foundo['id']
			if foundo in foundobjs:
				print('Will delete a duplicate statement.')
				results = site.post('wbremoveclaims', claim=guid, token=token)
				if results['success'] == 1:
					print('Wb remove duplicate claim for '+s+' ('+p+') '+o+': success.')
			else:
				foundobjs.append(foundo)
				#print("A statement #"+str(statementcount)+" for prop "+p+" is already there: "+foundo)

				if foundo == o or foundo == value:
					print('Found redundant triple '+s+' ('+p+') '+o+' >> Claim update skipped.')
					return guid

				elif p in card1props:
					print('('+p+') is a max 1 prop. Will replace statement.')

					while True:
						try:
							results = site.post('wbsetclaimvalue', token=token, claim=guid, snaktype="value", value=value)

							if results['success'] == 1:
								print('Claim update for '+s+' ('+p+') '+o+': success.')
								foundobjs.append(o)
								returnvalue = guid
								break
						except Exception as ex:
							if 'Invalid CSRF token.' in str(ex):
								print('Wait a sec. Must get a new CSRF token...')
								token = get_token()
							else:
								print('Claim update failed... Will try again.')
								time.sleep(4)

	if o not in foundobjs and value not in foundobjs: # must create new statement

		count = 0
		while count < 5:
			count += 1
			try:
				if dtype == "novalue":
					request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="novalue", bot=1)
				else:
					request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=1)

				if request['success'] == 1:

					claimId = request['claim']['id']
					print('Claim creation done: '+s+' ('+p+') '+o+'.')
					return claimId

			except Exception as ex:
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					token = get_token()
				else:
					print('Claim creation failed, will try again...\n'+str(ex))
					logging.error('Claim creation '+s+' ('+p+') '+o+' failed, will try again...\n', exc_info=True)
					time.sleep(4)

		print ('*** Claim creation operation '+s+' ('+p+') '+o+' failed 5 times... skipped.')
		logging.warning('Claim set operation '+s+' ('+p+') '+o+' failed 5 times... skipped.')
		return False
	else:
		return returnvalue



# set a Qualifier
def setqualifier(qid, prop, claimid, qualiprop, qualio, dtype):
	global token
	if dtype == "string" or dtype == "url":
		qualivalue = '"'+qualio.replace('"', '\\"')+'"'
	elif dtype == "item" or dtype =="wikibase-entityid":
		qualivalue = json.dumps({"entity-type":"item","numeric-id":int(qualio.replace("Q",""))})
	elif dtype == "time":
		qualivalue = json.dumps({
		"entity-type":"time",
		"time": qualio['time'],
	    "timezone": 0,
	    "before": 0,
	    "after": 0,
	    "precision": qualio['precision'],
	    "calendarmodel": "http://www.wikidata.org/entity/Q1985727"})
	elif dtype == "monolingualtext":
		qualivalue = json.dumps(qualio)
	elif dtype == "lexeme":
		print('Will try to write Lexeme as qualiobject: '+qualio)
		qualivalue = json.dumps({"entity-type":"lexeme","id":qualio,"numeric-id":int(qualio.replace("L",""))})
	if qualiprop in config.card1props:
		#print('Detected card1prop as qualifier.')
		existingclaims = getclaims(qid,prop)
		#print(str(existingclaims))
		qid = existingclaims[0]
		existingclaims = existingclaims[1]
		if prop in existingclaims:
			for claim in existingclaims[prop]:
				if claim['id'] != claimid:
					continue # skip other claims
				if "qualifiers" in claim:
					if qualiprop in claim['qualifiers']:
						existingqualihashes = {}
						for quali in claim['qualifiers'][qualiprop]:
							existingqualihash = quali['hash']
							existingqualivalue = quali['datavalue']['value']
							if isinstance(existingqualivalue, dict):
								if "time" in existingqualivalue:
									existingqualivalue = {"time":existingqualivalue['time'],"precision":existingqualivalue['precision']}
								if "text" in existingqualivalue and "language" in existingqualivalue:
									existingqualivalue = json.dumps(existingqualivalue)
							existingqualihashes[existingqualihash] = existingqualivalue
						#print('Found an existing '+qualiprop+' type card1 qualifier: '+str(list(existingqualihashes.values())[0]))
						allhashes = list(existingqualihashes.keys())
						done = False
						while (not done):
							if len(existingqualihashes) > 1:
								print('Found several qualis, but cardinality is 1; will delete all but the newest.')
								for delqualihash in allhashes:
									if delqualihash == allhashes[len(allhashes)-1]: # leave the last one intact
										print('Will leave intact this quali: '+existingqualihashes[delqualihash])
										existingqualihash = existingqualihashes[delqualihash]
									else:
										removequali(claimid,delqualihash)
										del existingqualihashes[delqualihash]
							elif len(existingqualihashes) == 1:
								done = True

						if str(list(existingqualihashes.values())[0]) in qualivalue:
							#print('Found duplicate value for card1 quali. Skipped.')
							return True
						if dtype == "time":
							if list(existingqualihashes.values())[0]['time'] == qualio['time'] and list(existingqualihashes.values())[0]['precision'] == qualio['precision']:
								#print('Found duplicate value for '+qualiprop+' type time card1 quali. Skipped.')
								return True

						print('New value to be written to existing card1 quali.')
						try:
							while True:
								setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, snakhash=existingqualihash, property=qualiprop, snaktype="value", value=qualivalue, bot=1)
								# always set!!
								if setqualifier['success'] == 1:
									print('Qualifier set ('+qualiprop+') '+qualivalue+': success.')
									return True
								print('Qualifier set failed, will try again...')
								logging.error('Qualifier set failed for '+prop+' ('+qualiprop+') '+qualivalue+': '+str(ex))
								time.sleep(2)

						except Exception as ex:
							if 'The statement has already a qualifier' in str(ex):
								print('The statement already has that object as ('+qualiprop+') qualifier: skipped writing duplicate qualifier')
								return False
	# not a max1quali >> write new quali in case value is different to existing value
	try:
		while True:
			setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, property=qualiprop, snaktype="value", value=qualivalue, bot=1)
			# always set!!
			if setqualifier['success'] == 1:
				print('Qualifier set ('+qualiprop+') '+qualivalue+': success.')
				return True
			print('Qualifier set failed, will try again...')
			logging.error('Qualifier set failed for '+prop+' ('+qualiprop+') '+qualivalue+': '+str(ex))
			time.sleep(2)

	except Exception as ex:
		if 'The statement has already a qualifier' in str(ex):
			print('The statement already has a ('+qualiprop+') '+qualivalue+': skipped writing duplicate qualifier')
			return False




	# claims = getclaims(qid,prop)
	# foundobjs = []
	# if bool(claims):
	# 	statementcount = 0
	# 	for claim in claims[prop]:
	# 		if claim['id'] == claimid:
	#
	try:
		while True:
			setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, property=qualiprop, snaktype="value", value=qualivalue, bot=1)
			# always set!!
			if setqualifier['success'] == 1:
				print('Qualifier set for '+qualiprop+': success: '+qualivalue)
				return True
			print('Qualifier set failed, will try again...')
			logging.error('Qualifier set failed for '+prop+' ('+qualiprop+') '+qualivalue+': '+str(ex))
			time.sleep(2)

	except Exception as ex:
		if 'The statement has already a qualifier' in str(ex):
			print('**** The statement already has a ('+qualiprop+') duplicate qualifier')
			return False




# set a Reference
def setref(claimid, refprop, refvalue, dtype):
	global token
	if dtype == "string" or dtype == "monolingualtext":
		refvalue = '"'+refvalue.replace('"', '\\"')+'"'
		valtype = "string"
	elif dtype == "url":
		# no transformation
		valtype = "string"
	elif dtype == "item" or dtype =="wikibase-entityid":
		refvalue = json.dumps({"entity-type":"item","numeric-id":int(refvalue.replace("Q",""))})
		valtype = "wikibase-entityid"
	snaks = json.dumps({refprop:[{"snaktype":"value","property":refprop,"datavalue":{"type":valtype,"value":refvalue}}]})
	while True:
		try:
			setref = site.post('wbsetreference', token=token, statement=claimid, index=0, snaks=snaks, bot=1)
			# always set at index 0!!
			if setref['success'] == 1:
				print('Reference set for '+refprop+': success.')
				return True
		except Exception as ex:
			#print(str(ex))
			if 'The statement has already a reference with hash' in str(ex):
				print('**** The statement already has a reference (with the same hash)')
				time.sleep(1)
			else:
				logging.error('Unforeseen exception: '+str(ex))
				print(str(ex))
				time.sleep(5)
			return False


		print('Reference set failed, will try again...')
		logging.error('Reference set failed for '+prop+' ('+refprop+') '+refvalue+': '+str(ex))
		time.sleep(2)

# Function for getting wikipedia url from wikidata qid (from https://stackoverflow.com/a/60811917)
def get_wikipedia_url_from_wikidata_id(wikidata_id, lang='en', debug=False):
	#import requests
	from requests import utils

	url = (
		'https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks/urls&ids='+wikidata_id+'&format=json')
	json_response = requests.get(url).json()
	if debug: print(wikidata_id, url, json_response)

	entities = json_response.get('entities')
	if entities:
		entity = entities.get(wikidata_id)
		if entity:
			sitelinks = entity.get('sitelinks')
			if sitelinks:
				if lang:
					# filter only the specified language
					sitelink = sitelinks.get(lang+'wiki')
					if sitelink:
						wiki_url = sitelink.get('url')
						if wiki_url:
							return requests.utils.unquote(wiki_url)
				else:
					# return all of the urls
					wiki_urls = {}
					for key, sitelink in sitelinks.items():
						wiki_url = sitelink.get('url')
						if wiki_url:
							wiki_urls[key] = requests.utils.unquote(wiki_url)
					return wiki_urls
	return None

#remove claim
def removeclaim(guid):
	guidfix = re.compile(r'^([QL]\d+)\-')
	guid = re.sub(guidfix, r'\1$', guid)
	global token
	done = False
	while (not done):
		try:
			results = site.post('wbremoveclaims', claim=guid, token=token, bot=1)
			if results['success'] == 1:
				print('Wb remove claim for '+guid+': success.')
				done = True
		except Exception as ex:
			print('Removeclaim operation failed, will try again...\n'+str(ex))
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			if 'invalid-guid' in str(ex):
				print('The guid to remove was not found.')
				done = True
			time.sleep(4)

#remove claim
def removequali(guid, hash):
	global token
	done = False
	while (not done):
		try:
			results = site.post('wbremovequalifiers', claim=guid, qualifiers=hash, token=token, bot=1)
			if results['success'] == 1:
				print('Wb remove qualifier success.')
				done = True
		except Exception as ex:
			print('Removeclaim operation failed, will try again...\n'+str(ex))
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			if 'invalid-guid' in str(ex):
				print('The guid to remove was not found.')
				done = True
			time.sleep(4)
