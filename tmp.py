import config
import awb

items = {
"P1" : "wikidata entity",
"P2" : "formatter url",
"P3" : "instance of",
"P4" : "subclass of",
"P5" : "place",
"P6" : "part of speech",
"P7" : "Elhuyar Dictionary ID",
"P8" : "where documented",
"P9" : "Ahotsak lemma",
"P10" : "Standard Basque lemma",
"P11" : "Ahotsak variant",
"P12" : "ETC lemma",
"P13" : "ETC form",
"P14" : "ETC counts",
"P15" : "Standard Basque form",
"P17" : "Ahotsak place",
"P18" : "Basque dialect",
"P19" : "from region"
}
for item in items:
	awb.setlabel(item, "en", items[item])
