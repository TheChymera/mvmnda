from datetime import datetime
from dateutil import tz
from pathlib import Path
from neuroconv.converters import SpikeGLXConverterPipe
import json
import re
import pynwb
import datetime
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

dir_path = "../../sourcedata/sub-M388/M388-2023-11-20_2_g0"
#dir_path = "/mnt/DATA/data/studies/manish/mvmnda/sourcedata/sub-pixelfiber/M387-2023-10-20_g0"
#dir_path = "../../sourcedata/M387-2023-10-20_g0"
converter = SpikeGLXConverterPipe(folder_path=dir_path)

m = re.match(".*?sub-(?P<subject>[a-zA-z0-9]+).*?","../../sourcedata/sub-M388/M388-2023-11-20_2_g0")
# add logic to fall back on expkeys

subject = m.groupdict()["subject"]

# Extract what metadata we can from the source files
metadata = converter.get_metadata()

session_start_time = metadata["NWBFile"]["session_start_time"].replace(tzinfo=tz.gettz("US/Eastern"))
metadata["NWBFile"].update(session_start_time=session_start_time)
session = (metadata["NWBFile"]["session_start_time"]).strftime("%Y%m%d%H%M%S")

#print(session)

# Maybe do data of birth rather than age
metadata["Subject"] = dict(
    subject_id=subject,
    sex="F",
    species="Mus musculus",
    age="P90D",
    #date_of_birth=session_start_time-age_delta,
)
# No idea why this needs to be done via `.update()`
metadata["NWBFile"].update(session_id=session)
#metadata["session_id"] = session
#metadata["NWBFile"] = dict(session_id=session)

#print(metadata)

#print(metadata)
#print(metadata["NWBFile"])
#
# Choose a path for saving the nwb file and run the conversion
##nwbfile_path = "/mnt/DATA/data/studies/manish/mvmnda/rawdata/my_spikeglx_session.nwb"
##converter.run_conversion(nwbfile_path=nwbfile_path, metadata=metadata)



nwbfile_path = "../nwbdata/outfile.nwb"
converter.run_conversion(nwbfile_path=nwbfile_path, metadata=metadata)
