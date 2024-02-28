from datetime import datetime
from dateutil import tz
from pathlib import Path
from neuroconv.converters import SpikeGLXConverterPipe
import glob
import json
import re
import pynwb
import datetime
import os

ABSPATH = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(ABSPATH)
os.chdir(THIS_DIR)

EXPKEY_PATTERN="*_keys.m"

try:
    SCRATCH_PATH = os.environ['SCRATCH_PATH']
except KeyError:
    SCRATCH_PATH = "~/.local/share/mvmnda/nwbdata/"
SCRATCH_PATH = os.path.abspath(os.path.expanduser(SCRATCH_PATH))
os.makedirs(SCRATCH_PATH, exist_ok=True)

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
            'DOB',
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

def get_expkeys_file(in_dir):
    expkeys_files = glob.glob(os.path.join(in_dir,EXPKEY_PATTERN))
    if len(expkeys_files) == 1:
        return expkeys_files[0]
    elif len(expkeys_files) >= 1:
        print("There should only be one ExpKeys file per experiment.")
        print(f"In the `{in_dir}` candidate directory the following ExpKeys pattern files were found:")
        for expkeys_file in expkeys_files:
            print(f"\t* `{expkeys_file}`")
        return False
    else:
        print(f"No ExpKeys file found under `{in_dir}`.")



def convert_all(base_dir):
    in_dir = os.path.abspath(os.path.expanduser(base_dir))

    # Is this a sensible criterion?
    spikeglx_dirs = [y for x in os.walk(base_dir) for y in glob.glob(os.path.join(x[0], '*_g0'))]
    for spikeglx_dir in spikeglx_dirs:
        # Only convert if we have ExpKeys
        if get_expkeys_file(spikeglx_dir):
            convert_measurement(spikeglx_dir)

def convert_measurement(in_dir, scratch_path=SCRATCH_PATH):
    expkeys_file = get_expkeys_file(in_dir)
    if not expkeys_file:
        raise ValueError("Cannot proceed without corresponding ExpKeys file.")

    expkeys = read_expkeys(expkeys_file)

    converter = SpikeGLXConverterPipe(folder_path=in_dir)

    m = re.match(".*?sub-(?P<subject>[a-zA-z0-9]+).*?", in_dir)
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
        date_of_birth=expkeys["DOB"],
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
