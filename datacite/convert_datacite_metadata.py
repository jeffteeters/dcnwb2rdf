import xml.etree.ElementTree as ET
import pprint
import json
import base64
import re


# script to convert datacite metadata in file ucbcrcns.json from XML format
# (included in base64 encoded field "xml") to JSON format and store in file
# crcns_datasets.json


pp = pprint.PrettyPrinter(indent=4)

file_name = "ucbcrcns.json"

# script to unpack file ucbcrcns.json
# uses api at: https://search.datacite.org/help.html

with open(file_name, "r") as fin:
    contents = fin.read()
                                                                                                                                                                                     
# import pdb; pdb.set_trace()

rj = json.loads(contents)
ds_items = rj['response']['docs']
print ("found %i datasets" % len(ds_items))

global ns
ns = { "datacite" : "http://datacite.org/schema/kernel-2.2" }

def clear_extra_spaces(text):
    ctext = re.sub("\n\s*", " ", text)
    ctext = ctext.strip()
    return ctext
    

def extract_datacite_parts(xml):
    # use ElementTree Element methods to extract parts from XML
    root = ET.fromstring(xml)
    dc_parts = {}
    # subjects
    sub_et = root.findall('datacite:subjects', ns)
    assert len(sub_et) == 1, "should be exactly one 'subjects', found %i" % len(sub_et)
    subject_list = sub_et[0].findall('datacite:subject', ns)
    subjects = [x.text for x in subject_list]
    dc_parts['subjects'] = subjects
    # description
    descr_et = root.findall('datacite:descriptions', ns)
    assert len(descr_et) == 1, "should be exactly one 'descriptions', found %i" % len(descr_et)
    descr = descr_et[0].findall('datacite:description', ns)
    assert len(descr) == 1, "should be exactly one 'descriptions', found %i" % len(descr)
    description = descr[0].text
    dc_parts['description'] = clear_extra_spaces(description)
    # titles
    title_et = root.findall('datacite:titles', ns)
    assert len(title_et) == 1, "should be exactly one 'titles', found %i" % len(title_et)
    titles = title_et[0].findall('datacite:title', ns)
    assert len(titles) == 2, "should be exactly two 'titles', found %i" % len(titles)
    title = titles[0].text
    assert "AlternativeTitle" == titles[1].attrib['titleType'], ("did not find AlternativeTitle in %s"
        % titles[1].attrib['titleType'])
    alt_title = titles[1].text
    dc_parts['title'] = clear_extra_spaces(title)
    alt_title_c = re.sub("CRCNS.org ", "", alt_title)  # strip "CRCNS.org " from alt_title
    dc_parts['alt_title'] = alt_title_c
    # publication year
    year_et = root.findall('datacite:publicationYear', ns)
    assert len(year_et) == 1, "should be exactly one 'publicationYear', found %i" % len(year_et)
    year = year_et[0].text
    dc_parts['publicationYear'] = year
    # creators
    creators_et = root.findall('datacite:creators', ns)
    assert len(creators_et) == 1, "should be exactly one 'creators', found %i" % len(creators_et)
    creators_list = creators_et[0].findall('datacite:creator', ns)
    assert len(creators_list) > 0, "should be one or more creators', found %i" % len(creators_list)
    creators = [ x.find('datacite:creatorName', ns).text for x in creators_list]
    dc_parts['creators'] = creators
    return dc_parts     

# crcns_datasets = []
crcns_datasets = {}
for dsi in ds_items:
    doi = dsi['doi']
    minted = dsi['minted']
    updated = dsi['updated']
    xml = base64.b64decode(dsi['xml'])
    ds_info = extract_datacite_parts(xml)
    alt_title = ds_info['alt_title']
    ds_info['doi'] = doi
    ds_info['minted'] = minted
    ds_info['updated'] = updated
    # crcns_datasets.append(ds_info)
    crcns_datasets[alt_title] = ds_info
#     print ("doi=%s, minted=%s, updated=%s, xml=%s" % (doi, minted, updated, xml))
#     pp.pprint(dc_parts)
#     import pdb; pdb.set_trace()

cds = json.dumps(crcns_datasets, sort_keys=True, indent=4)

with open("crcns_datasets.json", "w") as fout:
    fout.write(cds)