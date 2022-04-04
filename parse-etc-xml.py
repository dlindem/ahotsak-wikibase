import os
import sys
import re
import json
import traceback
import time
import config
from xml.etree import ElementTree

try:
	etctree = ElementTree.parse('D:/Ahotsak/ETC/2022-ETC-lemak-formak-utf8.xml')
except Exception as ex:
	print ('Error: file does not exist, or XML cannot be loaded.')
	print (str(ex))
	sys.exit()

root = etctree.getroot()
etclist = []
for fitxa in root:
	target = {}
	target['lema'] = fitxa.findall('lema')[0].text
	#print('Lema: '+target['lema'])
	target['lema_agerpenak'] = int(fitxa.findall('agerpenak')[0].text)
	target['kategoriak'] = fitxa.findall('kategoria')[0].text.split(' | ')
	target['formak'] = []
	for forma in fitxa.findall('formak')[0]:
		targetforma = {}
		#print('Forma: '+forma.text)
		targetforma['forma'] = forma.text
		targetforma['agerpenak'] = int(forma.findall('agerpenak')[0].text)
		target['formak'].append(targetforma)

	etclist.append(target)

with open('D:/Ahotsak/ETC/2022-ETC-lemak-formak.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(etclist, jsonfile, indent=2)
# with open('D:/FiloSarea/ahotsak_404ak.json', 'w', encoding="utf-8") as errorlistfile:
# 	json.dump(errorlist, errorlistfile, indent=2)
