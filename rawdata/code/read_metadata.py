from pynwb import NWBHDF5IO

# Replace 'your_file.nwb' with the actual path to your NWB file
nwb_file_path = '../sub-M388/sub-M388_obj-1tv1gbj_ecephys.nwb'

# Read the NWB file
with NWBHDF5IO(nwb_file_path, 'r') as io:
    nwbfile = io.read()

# Get all metadata fields as a dictionary
metadata_dict = nwbfile.fields

# Print or use the metadata dictionary as needed
print(metadata_dict)
print(metadata_dict["acquisition"])
