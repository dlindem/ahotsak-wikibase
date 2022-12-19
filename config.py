from config_private import awbuser as awbuser
from config_private import awbuserpass as awbuserpass

datafolder = "data/"

sparql_prefixes = """
PREFIX awb: <https://datuak.ahotsak.eus/entity/>
PREFIX adp: <https://datuak.ahotsak.eus/prop/direct/>
PREFIX ap: <https://datuak.ahotsak.eus/prop/>
PREFIX aps: <https://datuak.ahotsak.eus/prop/statement/>
PREFIX apq: <https://datuak.ahotsak.eus/prop/qualifier/>
PREFIX apr: <https://datuak.ahotsak.eus/prop/reference/>
"""
# Properties with constraint: max. 1 value
card1props = [
"P12",
"P13",
"P14",
"P19"
]
