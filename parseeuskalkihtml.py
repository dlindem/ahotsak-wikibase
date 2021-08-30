import os
import sys
import re
import json
import xml.etree.ElementTree as ET
import traceback
import time
import config



result = {}
errorlist = []

with open("D:/Ahotsak/euskalkiak/ahotsak_zuhaitza.html", 'r', encoding="utf-8") as htmlfile:
	html = htmlfile.read()
#print(html)
table = ET.fromstring(html)
for ul in table:
	for li in ul:
		print('First level text', li.text)
		print('First level xml', ET.dump(li))
		for a in li:
			litext = li.attrib['href']
			print(litext)
		for ul2 in li:
			for li2 in ul2:
				print('Second level', li2.text)
				for ul3 in li2:
					for li3 in ul3:
						print('Third level', li3.text)
	# for li in ul:
	# 	print('First level')
	# 	for ul in td:
	# 		for li in ul:
	# 			aldaera = li.find('strong').text
	# 			print(aldaera)
	# 			hitzak[aldaera] = []
	# 			hitzlist = li.find('ul')
	# 			for li2 in hitzlist:
	# 				hitz_block = li2.find('a').text
	# 				hitza = re.search('\n(\w+)', hitz_block).group(1)
	# 				hitzak[aldaera].append(hitza)
