# mapping of ahotsak - wikidata forms
import sparql
import time
from Levenshtein import distance
import tkinter as tk
from tkinter import simpledialog
import math
import os
import json
import config

# load ahotsak and etc lexemes (those pairs with forms for both only)
try:
	with open('D:/Ahotsak/aholid_etclid.json', 'r', encoding="utf-8") as lidfile:
		lids = json.load(lidfile)
except:
	print('lidfile not found, will get data now.')
	query = """
	PREFIX awb: <http://datuak.ahotsak.eus/entity/>
	PREFIX adp: <http://datuak.ahotsak.eus/prop/direct/>
	PREFIX ap: <http://datuak.ahotsak.eus/prop/>
	PREFIX aps: <http://datuak.ahotsak.eus/prop/statement/>
	PREFIX apq: <http://datuak.ahotsak.eus/prop/qualifier/>
	PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>

	select distinct ?aholexeme ?aholema ?etclexeme ?wdlid

	WHERE {
	  ?aholexeme adp:P3 awb:Q750;
	          adp:P10 ?etclexeme;
	          wikibase:lemma ?aholema.
	          filter exists (?aholexeme ontolex:lexicalForm ?ahoform .) # filters out lexemes with 0 forms
	  ?etclexeme adp:P1 ?wdlid .
	          filter exists (?etclexeme ontolex:lexicalForm ?etcform. )# filters out lexemes with 0 forms


	} """

	print("Waiting for SPARQL ...")
	sparqlresults = sparql.query("https://datuak.ahotsak.eus/query/sparql",query)
	#go through sparqlresults
	rowindex = 0
	lids = {}
	for row in sparqlresults:
		#time.sleep(0.5)
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		print('\nNow processing form ['+str(rowindex)+']:\n'+str(item))
		lids[item[0].replace("http://datuak.ahotsak.eus/entity/","")]={
		'aholema' : item[1],
		'etclid' : item[2].replace("http://datuak.ahotsak.eus/entity/",""),
		'wdlid' : item[3]}
	with open('D:/Ahotsak/aholid_etclid.json', 'w', encoding="utf-8") as lidfile:
		json.dump(lids, lidfile, indent=2)

for aholid in lids:
	etclid = lids[aholid]['etclid']
	# load ahotsak and ETC forms
	dir = 'D:/Ahotsak/formak'
	file_list = os.listdir(dir)
	if aholid+".json" in file_list:
		with open(dir+'/'+aholid+".json", "r", encoding="utf-8") as jsonfile:
			formsjson = json.load(jsonfile)
			ahoforms = formsjson['ahoforms']
			etcforms = formsjson['etcforms']
	else:
		query = """
		PREFIX awb: <http://datuak.ahotsak.eus/entity/>
		PREFIX adp: <http://datuak.ahotsak.eus/prop/direct/>
		PREFIX ap: <http://datuak.ahotsak.eus/prop/>
		PREFIX aps: <http://datuak.ahotsak.eus/prop/statement/>
		PREFIX apq: <http://datuak.ahotsak.eus/prop/qualifier/>
		PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>

		select ?formid ?word (group_concat(str(?grammarLabel);SEPARATOR="; ") as ?gram)

		WHERE {
		  {awb:"""+aholid+""" ontolex:lexicalForm ?form . ?form ontolex:representation ?word .} UNION
		  {awb:"""+etclid+""" ontolex:lexicalForm ?form . ?form ontolex:representation ?word .}
		  BIND(xsd:integer(strafter(str(?form),"-F")) as ?order)
		  BIND(strafter(str(?form),"http://datuak.ahotsak.eus/entity/") as ?formid)

		} GROUP BY ?formid ?word ?gram ORDER BY ?order
		"""
		#print(query)
		print("Waiting for AHOTSAK and ETC forms from SPARQL ...")
		sparqlresults = sparql.query("https://datuak.ahotsak.eus/query/sparql",query)
		#go through sparqlresults
		ahoforms = {}
		etcforms = {}
		for row in sparqlresults:
			item = sparql.unpack_row(row, convert=None, convert_type={})
			if item[0].startswith(aholid):
				ahoforms[item[0]] = {"word":item[1],"gram":item[1]}
			elif item[0].startswith(etclid):
				etcforms[item[0]] = {"word":item[1],"gram":item[2]}

		#print(str(etcforms))
		print('\nRead '+str(len(ahoforms))+' AHOTSAK forms for lemma '+aholid+'.')
		print('Read '+str(len(etcforms))+' ETC forms for lemma '+etclid+'.')
		with open(dir+'/'+aholid+".json", "w", encoding="utf-8") as jsonfile:
			json.dump({'ahoforms': ahoforms, 'etcforms': etcforms}, jsonfile, indent=2)

	for ahoform in ahoforms:
		ahoword = ahoforms[ahoform]['word']
		#get levenshtein distances
		zerodistcount = 0
		for etcform in etcforms:
			#print(etcform)
			#print(etcforms[etcform]['word'],ahoword,str(distance(etcforms[etcform]['word'],ahoword)))
			lvdist = distance(etcforms[etcform]['word'],ahoword)
			if lvdist == 0:
				zerodistcount += 1
				zerodistform = etcform
			etcforms[etcform]['dist'] = str(lvdist)

		if zerodistcount == 1:
			print('*** Here we have one zero distance form, mapped by default: '+zerodistform+' ('+etcforms[zerodistform]['word']+')')
			mappedform = zerodistform
		else:

			gui = tk.Tk()

			wrapper1 = tk.LabelFrame(gui)
			wrapper2 = tk.LabelFrame(gui)

			# wdcanvas = tk.Canvas(wrapper2)
			# wdcanvas.pack(side="left", fill="none", expand="yes")
			#
			# wdframe = tk.Frame(wdcanvas)
			# wdcanvas.create_window((0,0), window=wdframe, anchor="nw")
			wrapper1.pack(fill = "both", expand="yes", padx=10, pady=10)
			wrapper2.pack(fill = "both", expand="yes", padx=10, pady=10)


			# def buttonpress(function, *args):
			# 	value = function(*args)
			mappedform = None
			newform = None
			def showChoice():
				global mappedform
				global newform
				choice = v.get()
				if choice == "F0":
					print('Form not listed.')
					newform = simpledialog.askstring("Input", "Enter new form not listed below", parent=gui)
				else:
					print('Selection is: '+choice,etcforms[choice]['word'])
					mappedform = choice
				gui.destroy()

			v = tk.StringVar(value="F1")

			tk.Radiobutton(wrapper2,
			text = "FORM NOT LISTED",
			variable = v,
			command = showChoice,
			value = "F0"
			).grid(row = 1, column = 1)


			ldistance = 0
			count = 1
			done = False
			while count < len(etcforms)+1:
				for form in etcforms:

					if int(etcforms[form]['dist']) == ldistance:
						if count < 10:
							wdrow = count+1
							wdcolumn = 1
						else:
							wdrow = int(str(count)[1])+1
							wdcolumn = int(count/10)+1
						#print(str(ldistance)+': '+etcforms[form]['word'], str(wdrow), str(wdcolumn))
						tk.Radiobutton(wrapper2,
						text = etcforms[form]['word']+' ('+str(ldistance)+')\n'+str(etcforms[form]['gram']),
						variable = v,
						command = showChoice,
						value = form
						).grid(row = wdrow, column = wdcolumn)
						count += 1
				ldistance += 1

			# answer = v.get()
			# if answer != 0:
			# 	print(str(answer))

			gui.geometry("1600x800")
			gui.resizable(False, False)
			gui.title("Ahotsak Wikidata Form Mapping")
			tk.Label(wrapper1, text="Form to be mapped: "+ahoword).pack()

			gui.mainloop()


			print('Mapped form: '+str(mappedform))
			print('New form: '+str(newform))

		with open('D:/Ahotsak/form_mappings/mappings.jsonl', "a", encoding="utf-8") as mappingfile:
			if mappedform:
				result = {"aholid": aholid,"ahoform": ahoform, "ahoword": ahoword, "etcform": mappedform, "etclid": mappedform.split("-")[0]}
			elif newform:
				result = {"aholid": aholid,"ahoform": ahoform, "ahoword": ahoword, "newform": newform}
			mappingfile.write(json.dumps(result)+'\n')

		print('\nFinished this form.\n')
