import sys
import os
#sys.path.insert(1, os.path.realpath(os.path.pardir))
import time
import json
import requests
import csv
import awb
import config


print ('This is to copy multilingual labels from wikidata, for the following languages:')

allowed_languages = ['en']
# for iso3lang in langmapping.langcodemapping: # gets LexVoc elexis languages
# 	allowed_languages.append(langmapping.getWikiLangCode(iso3lang))
# print(str(allowed_languages))

with open(config.datafolder+'tmp/items_wdqids.txt', 'r') as infile:
	items_to_update = infile.read().split('\n')
print('\n'+str(len(items_to_update))+' items will be updated.')

with open(config.datafolder+'tmp/items_wdqids_done.txt', 'r') as donefile:
	done_items = donefile.read().split('\n')

itemcount = 0
for line in items_to_update:
	awbqid = line.split('\t')[0]
	wdqid = line.split('\t')[1]
	if awbqid in done_items:
		print('\nItem ['+str(itemcount)+'] has been done in a previous run.')
		continue
	# wdqid = awb.wdids[awbqid]
	print('\nItem ['+str(itemcount)+'], '+str(len(items_to_update)-itemcount)+' items left.')
	print('Will now get labels for awb item: '+awbqid+' from wdItem: '+wdqid)
	done = False
	while (not done):
		try:
			r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&ids="+wdqid).json()
			#print(str(r))
			if "labels" in r['entities'][wdqid]:
				for labellang in r['entities'][wdqid]['labels']:
					if labellang in allowed_languages:
						value = r['entities'][wdqid]['labels'][labellang]['value']
						existinglabel = awb.getlabel(awbqid,labellang)
						if not existinglabel:
							awb.setlabel(awbqid,labellang,value)
						else:
							if existinglabel.lower() != value.lower():
								awb.setlabel(awbqid,labellang,value, type="alias")
				done = True

		except Exception as ex:
			print('Wikidata: Label copy operation failed, will try again...\n'+str(ex))
			time.sleep(4)

	itemcount += 1
	with open(config.datafolder+'tmp/items_wdqids_done.txt', 'a') as outfile:
		outfile.write(awbqid+'\n')
