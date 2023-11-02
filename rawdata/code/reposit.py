from datetime import datetime
from dateutil import tz
from pathlib import Path
from neuroconv.converters import SpikeGLXConverterPipe

#folder_path = "/mnt/DATA/data/studies/manish/mvmnda/sourcedata/sub-pixelfiber/ses-01"
#folder_path = "/mnt/DATA/data/studies/manish/mvmnda/sourcedata/M387-2023-10-20_g0/M387-2023-10-20_g0_imec0/M387-2023-10-20_g0_tcat.imec0.ap.bin"
folder_path = "/mnt/DATA/data/studies/manish/mvmnda/sourcedata/M387-2023-10-20_g0"
converter = SpikeGLXConverterPipe(folder_path=folder_path)

# Extract what metadata we can from the source files
metadata = converter.get_metadata()
# For data provenance we add the time zone information to the conversion
#session_start_time = metadata["NWBFile"]["session_start_time"].replace(tzinfo=tz.gettz("US/Pacific"))
#metadata["NWBFile"].update(session_start_time=session_start_time)

# Choose a path for saving the nwb file and run the conversion
nwbfile_path = "/mnt/DATA/data/studies/manish/mvmnda/rawdata/my_spikeglx_session.nwb"
converter.run_conversion(nwbfile_path=nwbfile_path, metadata=metadata)