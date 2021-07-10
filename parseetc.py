import os
import sys
import re
import json
import traceback
import time
import config



result = {}
errorlist = []
dir = 'D:\Ahotsak\ETC'
for entry in os.scandir(dir):
	if entry.path.endswith(".html") and entry.is_file():
		print(entry.path)
		titles = re.search('(L\d+)_([^\.]+).html', entry.path)
		etc_bilaketa = titles.group(2)
		aholid = titles.group(1)
		result[etc_bilaketa] = {'etc_bilaketa': etc_bilaketa, 'aholid': aholid, 'filepath' : entry.path}

		with open(entry.path, 'r', encoding="ascii", errors="surrogateescape") as htmlfile:
			html = htmlfile.read()
		#print(html)
		try:
			content_block = html.split('<div class="emaitzaTitu">Formak</div>')
			formak_block = content_block[1].split('<div class="klear"></div>')[0]
			#print(aldaerak_block)
			agerraldiak_data = re.compile('<div class="agerpenak">([\.\d]+) agerraldi</div>')
			agerraldiak = agerraldiak_data.findall(content_block[0])
			formak_data = re.compile(' id="-([^;]+);x[^>]+></div>([\d\.]+)')
			formak = formak_data.findall(formak_block)
			#print(str(formak))
			etc_formak = []
			for formatuple in formak:
				etc_formak.append({"forma":formatuple[0].replace("\udcc3\udcb1","ñ"),"agerraldi":int(formatuple[1].replace(".",""))})
			result[etc_bilaketa]['etc_agerraldiak'] = int(agerraldiak[0].replace(".",""))
			result[etc_bilaketa]['formak'] = etc_formak
		except Exception as ex:
			traceback.print_exc()
			result[etc_bilaketa]['etc_agerraldiak'] = 0
			#ime.sleep(3)
			#errorlist.append({'lid':lid,'lemma':lemma})

with open('D:/Ahotsak/ETC/formak.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(result, jsonfile, indent=2)
# with open('D:/FiloSarea/ahotsak_404ak.json', 'w', encoding="utf-8") as errorlistfile:
# 	json.dump(errorlist, errorlistfile, indent=2)
