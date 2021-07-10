datafolder = "D:/Ahotsak/"

awbuser = "DavidL_bot"
with open(datafolder+'wikibase/DavidL_bot_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	awbuserpass = pwdfile.read()

# with open(datafolder+'zoteroapi/zotero_api_key.txt', 'r', encoding='utf-8') as pwdfile:
# 	zotero_api_key = pwdfile.read()

sparql_prefixes = """
PREFIX awb: <http://datuak.ahotsak.eus/entity/>
PREFIX adp: <http://datuak.ahotsak.eus/prop/direct/>
PREFIX ap: <http://datuak.ahotsak.eus/prop/>
PREFIX aps: <http://datuak.ahotsak.eus/prop/statement/>
PREFIX apq: <http://datuak.ahotsak.eus/prop/qualifier/>
PREFIX apr: <http://datuak.ahotsak.eus/prop/reference/>
"""
# Properties with constraint: max. 1 value
max1props = [
#"P1"
]
