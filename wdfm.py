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

# load dialectal forms
query = """
PREFIX awb: <http://datuak.ahotsak.eus/entity/>
PREFIX adp: <http://datuak.ahotsak.eus/prop/direct/>
PREFIX ap: <http://datuak.ahotsak.eus/prop/>
PREFIX aps: <http://datuak.ahotsak.eus/prop/statement/>
PREFIX apq: <http://datuak.ahotsak.eus/prop/qualifier/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>

select ?aholexeme ?aholema ?lexemabatua ?lemabatua ?wdlid ?form ?word #(group_concat(str(?grammarLabel);SEPARATOR="; ") as ?gram)

WHERE {
  ?aholexeme adp:P3 awb:Q750;
          adp:P10 ?lexemabatua;
          wikibase:lemma ?aholema;
          ontolex:lexicalForm ?form .
  ?lexemabatua adp:P1 ?wdlid ;
             wikibase:lemma ?lemabatua .
  ?form ontolex:representation ?word .

} """

print("Waiting for SPARQL ...")
sparqlresults = sparql.query("https://datuak.ahotsak.eus/query/sparql",query)
#go through sparqlresults
rowindex = 0
for row in sparqlresults:
	#time.sleep(0.5)
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing form ['+str(rowindex)+']:\n'+str(item))
	aholid = item[0].replace("http://datuak.ahotsak.eus/entity/","")
	aholema = item[1]
	lexemabatua = item[2].replace("http://datuak.ahotsak.eus/entity/","")
	lemabatua = item[3]
	wdlid = item[4]
	ahoform = item[5].replace("http://datuak.ahotsak.eus/entity/","")
	ahoword = item[6]

	# load wd forms
	dir = 'D:/Ahotsak/wikidata/wdlexemak'
	file_list = os.listdir(dir)
	if wdlid+".json" in file_list:
		with open(dir+'/'+wdlid+".json", "r", encoding="utf-8") as jsonfile:
			wdforms = json.load(jsonfile)
	else:
		query = """
		PREFIX wd: <http://www.wikidata.org/entity/>
		PREFIX wdt: <http://www.wikidata.org/prop/direct/>
		PREFIX wikibase: <http://wikiba.se/ontology#>
		PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>

		select ?order ?form ?word (group_concat(str(?grammarLabel);SEPARATOR="; ") as ?gram)

		WHERE {
		  wd:"""+wdlid+""" ontolex:lexicalForm ?form .
		  ?form ontolex:representation ?word .
		  OPTIONAL{?form wikibase:grammaticalFeature ?grammar .
		  ?grammar rdfs:label ?grammarLabel .
		  filter (lang(?grammarLabel)="eu")}
		  BIND(xsd:integer(strafter(str(?form),"-F")) as ?order)

		} GROUP BY ?order ?form ?word ?gram ORDER BY ?order
		"""
		#print(query)
		print("Waiting for wikidata SPARQL ...")
		sparqlresults = sparql.query("https://query.wikidata.org/sparql",query)
		#go through sparqlresults
		wdforms = {}
		for row in sparqlresults:
			item = sparql.unpack_row(row, convert=None, convert_type={})
			wdforms["F"+str(item[0])] = {"form":item[1],"word":item[2],"gram":item[3]}
		#print(str(wdforms))
		print('\nRead '+str(len(wdforms))+' forms for lemma '+wdlid+'.')
		with open(dir+'/'+wdlid+".json", "w", encoding="utf-8") as jsonfile:
			json.dump(wdforms, jsonfile, indent=2)

	#get levenshtein distances
	for wdform in wdforms:
		print(wdform)
		print(wdforms[wdform]['word'],ahoword,str(distance(wdforms[wdform]['word'],ahoword)))
		wdforms[wdform]['dist'] = str(distance(wdforms[wdform]['word'],ahoword))



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
			print('Selection is: '+choice,wdforms[choice]['word'])
			mappedform = wdforms[choice]['form']
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
	while count < len(wdforms)+1:
		for form in wdforms:

			if int(wdforms[form]['dist']) == ldistance:
				if count < 10:
					wdrow = count+1
					wdcolumn = 1
				else:
					wdrow = int(str(count)[1])+1
					wdcolumn = int(count/10)+1
				print(str(ldistance)+': '+wdforms[form]['word'], str(wdrow), str(wdcolumn))
				tk.Radiobutton(wrapper2,
				text = wdforms[form]['word']+' ('+str(ldistance)+')\n'+wdforms[form]['gram'],
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
		result = {"aholid": aholid,"ahoform": ahoform, "ahoword": ahoword, "wdform": mappedform, "newform": newform, "lexemabatua": lexemabatua}
		mappingfile.write(json.dumps(result)+'\n')

	print('\nFinished this form.')
