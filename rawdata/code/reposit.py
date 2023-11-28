from datetime import datetime
from dateutil import tz
from pathlib import Path
from neuroconv.converters import SpikeGLXConverterPipe
import json

dir_path = "/mnt/DATA/data/studies/manish/mvmnda/sourcedata/Ach_DualPixel_7_14_23/Ach_DualPixel_7_14_23_g0"
#dir_path = "/mnt/DATA/data/studies/manish/mvmnda/sourcedata/sub-pixelfiber/M387-2023-10-20_g0"
#dir_path = "../../sourcedata/M387-2023-10-20_g0"
converter = SpikeGLXConverterPipe(folder_path=dir_path)

# Extract what metadata we can from the source files
metadata = converter.get_metadata()

# The following doesn't work as per the guide ( https://neuroconv.readthedocs.io/en/main/conversion_examples_gallery/recording/spikeglx.html#single-stream ), apparently no session_start_time is read in:
#session_start_time = metadata["NWBFile"]["session_start_time"].replace(tzinfo=tz.gettz("US/Pacific"))
# So we do:
session_start_time = datetime.now(tz.tzlocal())
metadata["NWBFile"].update(session_start_time=session_start_time)

# Choose a path for saving the nwb file and run the conversion
nwbfile_path = "/mnt/DATA/data/studies/manish/mvmnda/rawdata/my_spikeglx_session.nwb"
converter.run_conversion(nwbfile_path=nwbfile_path, metadata=metadata)
