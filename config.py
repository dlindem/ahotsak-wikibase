datafolder = "D:/Ahotsak/"

awbuser = "DavidL_bot"

# with open(datafolder+'zoteroapi/zotero_api_key.txt', 'r', encoding='utf-8') as pwdfile:
# 	zotero_api_key = pwdfile.read()

sparql_prefixes = """
PREFIX awb: <http://datuak.ahotsak.eus/entity/>
PREFIX adp: <http://datuak.ahotsak.eus/prop/direct/>
PREFIX ap: <http://datuak.ahotsak.eus/prop/>
PREFIX aps: <http://datuak.ahotsak.eus/prop/statement/>
PREFIX apq: <http://datuak.ahotsak.eus/prop/qualifier/>
"""
# Properties with constraint: max. 1 value
max1props = []
