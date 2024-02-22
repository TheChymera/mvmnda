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

def read_expkeys(
    in_file,
    ):
    """
    Read ExpKeys format, which is an internal convention of the Dartmouth PBS van der Meer lab.

    Parameters
    ----------

    in_file: str, optional
        Path to ExpKeys file, will have a “.m” format.
    """

    raw_fields = [
            'species',
            'genetics',
            'subject_id',
            'hemisphere',
            'experimenter',
            'weight',
            'probeDepth',
            'date',
            'target',
            'light_source',
            'wavelength',
            'probeType',
            'probeID',
            'HSID',
            'patch_cord_dia',
            'patch_cord_NA',
            'probe_fiber_dia',
            'probe_fiber_NA',
            'max_power',
            'output_power_calib',
            'dial_values_calib',
            'dial_value',
            'light_power',
            'stim_mode',
            'ISI',
            'short_stim_pulse_width',
            'long_stim_pulse_width',
            'pre_trial_stim_on',
            'trial_stim_on',
            'post_trial_stim_on',
            'long_stim_on',
            'stim_off',
            'pre_baseline_times',
            'pre_stim_times',
            'stim_times',
            'post_baseline_times',
            'post_stim_times',
            'long_stim_times',
            'recording_times',
            'notes',
            'isReferenceRecordedSeparately',
            'hasSpecialStim',
            'LFP_channels',
            'ref_channels',
    ]
    
    p1 = re.compile('ExpKeys.(.+?)=')
    p2 = ['=(.+?)";', '=(.+?)};', '=(.+?)];', '=(.+?);']  # The order is important
    p2 = [re.compile(x) for x in p2]

    in_file = os.path.abspath(os.path.expanduser(in_file))

    out_dict = {}
    with open(in_file, 'r') as f:
        for line in f:
            m = re.search(p1, line)
            if m:
                key = m.group(1).strip()
                if key in raw_fields:
                    for iP in range(4):
                        m = re.search(p2[iP], line)
                        if m:
                            if iP == 0: # This is a simple string
                                value = m.group(1).strip(" \"")
                            elif iP == 1: # This is a 1-D list
                                temp = m.group(1).strip()[1:]
                                value = [x.strip()[1:-1] for x in temp.split(',')]
                            elif iP == 2: # This can be a nested loop, FML AARRGGGHHHHHHH
                                temp = m.group(1).strip()[1:]
                                value = [float(x.strip()) for x in temp.split(',')]
                                #value = "I don't know man"
                            else:   # iP has to be 3, and this is either a number, or true/false
                                temp = m.group(1).strip()
                                if temp == 'true':
                                    value = True
                                elif temp == 'false':
                                    value = False
                                else: # definitely a number
                                    value = float(m.group(1).strip())
                            out_dict[key] = value
                            break
                else:
                    continue

        #print(json.dumps(out_dict))
        return out_dict


try:
    scratch_path = os.environ['MVMNDA_RAWDATA_SCRATCH_PATH']
except KeyError:
    scratch_path = "~/.local/share/mvmnda/rawdata/"
    scratch_path = os.path.join(scratch_path, "{datetime.datetime.now().isoformat()}")
scratch_path = os.path.abspath(os.path.expanduser(scratch_path))
os.makedirs(scratch_path, exist_ok=True)

dir_path = "../../sourcedata/sub-M388/M388-2023-11-20_2_g0"
converter = SpikeGLXConverterPipe(folder_path=dir_path)

m = re.match(".*?sub-(?P<subject>[a-zA-z0-9]+).*?","../../sourcedata/sub-M388/M388-2023-11-20_2_g0")
# add logic to fall back on expkeys

subject = m.groupdict()["subject"]

# Extract what metadata we can from the source files
metadata = converter.get_metadata()

# Set timezone
session_start_time = metadata["NWBFile"]["session_start_time"].replace(tzinfo=tz.gettz("US/Eastern"))
metadata["NWBFile"].update(session_start_time=session_start_time)
session = (metadata["NWBFile"]["session_start_time"]).strftime("%Y%m%d%H%M%S")

# Maybe do date of birth rather than age
metadata["Subject"] = dict(
    subject_id=subject,
    sex="F",
    species="Mus musculus",
    age="P90D",
    #date_of_birth=session_start_time-age_delta,
)
# No idea why this needs to be done via `.update()`
metadata["NWBFile"].update(session_id=session)

# Read in Matt's lab “keys” files.





#print(metadata)

#print(metadata)
#print(metadata["NWBFile"])
#
# Choose a path for saving the nwb file and run the conversion
##nwbfile_path = "/mnt/DATA/data/studies/manish/mvmnda/rawdata/my_spikeglx_session.nwb"
##converter.run_conversion(nwbfile_path=nwbfile_path, metadata=metadata)

nwbfile_path = os.path.join(scratch_path,f"ses-{metadata['NWBFile']['session_id']}_sub-{metadata['Subject']['subject_id']}.nwb")
converter.run_conversion(nwbfile_path=nwbfile_path, metadata=metadata)
