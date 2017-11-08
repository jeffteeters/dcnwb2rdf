
import requests
import pprint
import json
import base64
pp = pprint.PrettyPrinter(indent=4)

# script to fetch file ucbcrcns.json from DataCite
# uses api at: https://search.datacite.org/help.html


arx="http://search.datacite.org/api?q=datacentre_symbol:cdl.ucbcrcns&fl=doi,minted,updated,xml&fq=has_metadata:true&fq=is_active:true&rows=1000&start=0&sort=updated+asc&wt=json"
r = requests.get(arx)

rj = json.loads(r.text)
rjs = json.dumps(rj, sort_keys=True, indent=4)

with open("ucbcrcns.json", "w") as fout:
    fout.write(rjs)
