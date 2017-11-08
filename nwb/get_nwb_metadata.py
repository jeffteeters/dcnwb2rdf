# extract nwb metadata
import os
import json
import h5py

# extract some metadata from NWB files (version 1.0.6), store the
# metadata in a JSON file that can be converted to RDF using
# the Semantic Framework software

# nwb files are assumed to be stored under directory:
#    nwb_top_dir = "../nwb_datasets"
# inside directories:
#    nwb_dirs = ('alm-1', 'ssc-2', 'ssc-7')
# output file is:
#    output_file = "nwb_metadata.json"

# The nwb files can be obtained from CRCNS.org.  For
# the runs done with the poster, the following nwb files
# were included:
# $ ls ../nwb_datasets/alm-1/
# data_structure_ANM210862_20130627.nwb	data_structure_ANM218453_20131017.nwb	data_structure_ANM219253_20140121a.nwb
# $ ls ../nwb_datasets/ssc-2
# an194181_2013_01_20_data_struct.nwb	an198503_2013_03_13_data_struct.nwb	an229716_2013_12_05b_data_struct.nwb
# $ ls ../nwb_datasets/ssc-7
# data (all files, total of 148)



def get_dsv(f, ds_path):
    # get hdf5 dataset value at ds_path or return ""
    try:
        value = f[ds_path].value
    except ValueError as e:
        value = ""
    return value

    
def get_nwb_datatypes(f):
    # return list of datatypes present in nwb file general group
    datatypes = (
        "intracellular_ephys",
        "extracellular_ephys",
        "optophysiology",
        "optogenetics")
    foundtypes = []
    for datatype in datatypes:
        if datatype in f['general']:
            foundtypes.append(datatype)
    return sorted(foundtypes)

interface_types = set([
    "BehavioralEvents",
    "BehavioralEpochs",
    "BehavioralTimeSeries",
    "Clustering",
    "ClusterWaveforms",
    "CompassDirection",
    "DfOverF",
    "EventDetection",
    "EventWaveform",
    "EyeTracking",
    "FeatureExtraction",
    "FilteredEphys",
    "Fluorescence",
    "ImageSegmentation",
    "ImagingRetinotopy",
    "LFP",
    "MotionCorrection",
    "Position",
    "PupilTracking",
    "UnitTimes"]
    )
def get_nwb_interfaces(f):
    # get list of interfaces from attribute on each module
    global interface_types
    found_interfaces = set()
    for mod in f['processing']:
        ifl = f['processing'][mod].attrs['interfaces']
        ifls = set(ifl)
        assert ifls < interface_types
        found_interfaces |= ifls
    return sorted(found_interfaces)


def get_h5_metadata(path):
    # extract metadata from nwb file located at path
    f = h5py.File(path)
    info = {}
    info['datatypes'] = ",".join(get_nwb_datatypes(f))
    info['interfaces'] = ",".join(get_nwb_interfaces(f))
    si = {}
    si['species'] = get_dsv(f, 'general/subject/species')
    si['sex'] = get_dsv(f,'general/subject/sex')
    si['genotype'] = get_dsv(f,'general/subject/genotype')
    info['subject'] = si
    info['virus'] = get_dsv(f,'general/virus')
    info['experimenter'] = get_dsv(f,'general/experimenter')
    f.close()
    return info

def extract_nwb_metadata(nwb_top_dir, output_file):
    # extract nwb_metadata, save in output_file
    nwb_dirs = ('alm-1', 'ssc-2', 'ssc-7')
    output = {}
    for key in nwb_dirs:
        file_count = 0
        top_dir = os.path.join(nwb_top_dir, key)
        for root, dirs, files in os.walk(top_dir):
            for file in files:
                if file.endswith(".nwb"):
                    file_count += 1
                    path = os.path.join(root, file)
                    short_path = path[len(nwb_top_dir) + 1:]
                    info = {"key": key, "file_name": file, "path": short_path}
                    # print short_path
                    info.update(get_h5_metadata(path))
                    fkey = "%s_%i" % (key, file_count)
                    fkey = fkey.replace("-", "")
                    output[fkey] = info
    metadata = json.dumps(output, sort_keys=True, indent=4)
    with open(output_file, "w") as fout:
        fout.write(metadata)
    
if __name__ == "__main__":
    output_file = "nwb_metadata.json"
    nwb_top_dir = "../nwb_datasets"
    extract_nwb_metadata(nwb_top_dir, output_file)
    
