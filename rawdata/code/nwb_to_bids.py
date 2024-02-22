from pynwb import NWBHDF5IO
from pynwb.ecephys import ElectricalSeries
from glob import glob
import os
import json
import pandas as pd
import shutil


def extract_metadata(filepath: str) -> dict:

    with NWBHDF5IO(filepath, load_namespaces=True) as io:
        nwbfile = io.read()

        subject = nwbfile.subject

        probes = set([x.device for x in nwbfile.electrodes["group"][:]])

        ess = [
            x for x in nwbfile.objects.values()
            if isinstance(x, ElectricalSeries)
        ]

        metadata = {
            "general_ephys": {
                "InstitutionName": nwbfile.institution,
            },
            "subject": {
                "subject_id": "sub-" + subject.subject_id,
                "species": subject.species,
                "strain": subject.strain,
                "birthday": subject.date_of_birth,
                "age": subject.age,
                "sex": subject.sex,
            },
            "session": {
                "session_id": "ses-" + nwbfile.session_id,
                "number_of_trials": len(nwbfile.trials) if nwbfile.trials else None,
                "comments": nwbfile.session_description,
            },
            "probes": [
                {
                    "probe_id": probe.name,
                    "type": "unknown",
                    "description": probe.description,
                    "manufacturer": probe.manufacturer,
                }
                for probe in probes
            ],
            "contacts": [
                {
                    "contact_id": contact.index[0],
                    "probe_id": contact.group.iloc[0].device.name,
                    #TODO "impedance": contact["imp"].iloc[0] if contact["imp"].iloc[0] > 0 else None,
                    "location": contact["location"].iloc[0] if contact["location"].iloc[0] not in ("unknown",) else None,
                }
                for contact in nwbfile.electrodes
            ],
            "channels": [
                {
                    "channel_id": contact.index[0],
                    "contact_id": contact.index[0],
                    "type": "EXT",
                    "unit": "V",
                    "sampling_frequency": ess[0].rate,
                    "gain": ess[0].conversion,
                }
                for contact in nwbfile.electrodes
            ]
        }
    
    return metadata

def unique_list_of_dicts(data):
    # Convert to set of tuples
    unique_data = set(tuple(d.items()) for d in data)
    
    # Convert back to list of dictionaries
    unique_list_of_dicts = [dict(t) for t in unique_data]
    
    return unique_list_of_dicts


def drop_false_cols(df):
    for col in df.columns:
        if not any(df[col][:]):
            df.drop(columns=[col], inplace=True)

path = "../"
#path = "/Volumes/Extreme Pro/neural_data/dandisets/000044"

nwb_files = glob(path + "/sub-*/ses-*/*.nwb")

all_metadata = {x: extract_metadata(x) for x in nwb_files}

# root

out_path = "bids_output"

#if not os.path.exists(out_path):
#    os.mkdir(out_path)
os.makedirs(out_path, exist_ok=True)

# participants

# create particiant table

subjects = unique_list_of_dicts(
    #[x["participant"] for x in all_metadata.values()]
    [x["subject"] for x in all_metadata.values()]
)

df = pd.DataFrame(subjects)

drop_false_cols(df)

df.to_csv(os.path.join(out_path, "participants.tsv"), sep="\t", index=False)


# create particiant json
default_subjects_json = {
    "subject_id": {"Description": "Unique identifier of the subject"},
    "species": {"Description": "The binomial species name from the NCBI Taxonomy"},
    "strain": {"Description": "Identifier of the strain"},
    "birthdate": {"Description": "Day of birth of the participant in ISO8601 format"},
    "age": {"Description": "Age of the participant at time of recording", "Units": "days"},
    "sex": {"Description": "Sex of participant"},
}

subjects_json = {k: v for k, v in default_subjects_json.items() if k in df.columns}

with open(os.path.join(out_path, "participants.json"), "w") as json_file:
    json.dump(subjects_json, json_file, indent=4)


# sessions

default_session_json = {
   "session_quality": {
      "LongName": "General quality of the session",
      "Description": "Quality of the session",
      "Levels": {
         "Bad": "Bad quality, should not be considered for further analysis",
         "ok": "Ok quality, can be considered for further analysis with care",
         "good": "Good quality, should be used for analysis",
         "Excellent": "Excellent quality, extraordinarily good session",
      }
   },
   "data_quality": {
      "LongName": "Quality of the recorded signals",
      "Description": "Quality of the recorded signals",
      "Levels": {
         "Bad": "Bad quality, should not be considered for further analysis",
         "ok": "Ok quality, can be considered for further analysis with care",
         "good": "Good quality, should be used for analysis",
         "Excellent": "Excellent quality, extraordinarily good session",
      },
   },
   "number_of_trials": {
      "LongName": "Number of trials in this session",
      "Description": "Count of attempted trials in the session (integer)",
   },
   "comment": {
      "LongName": "General comments",
      "Description": "General comments by the experimenter on the session",
   },
}

for subject in subjects:
    subject_id = subject["subject_id"]

    os.makedirs(os.path.join(out_path, subject_id), exist_ok=True)

    for metadata in all_metadata.values():
        sessions = [
            x["session"] for x in all_metadata.values() if
            x["subject"]["subject_id"] == subject_id
        ]

        df = pd.DataFrame(sessions)
        drop_false_cols(df)

        df.to_csv(os.path.join(out_path, subject_id, "sessions.tsv"), sep="\t", index=False)

        session_json = {k: v for k, v in default_session_json.items() if k in df.columns}

        with open(os.path.join(out_path, subject_id, "sessions.json"), "w") as json_file:
            json.dump(session_json, json_file, indent=4)

# contacts, probes, and channels

for metadata in all_metadata.values():

    session_id = metadata["session"]["session_id"]
    subject_id = metadata["subject"]["subject_id"]

    os.makedirs(os.path.join(out_path, subject_id, session_id), exist_ok=True)
    os.makedirs(os.path.join(out_path, subject_id, session_id, "ephys"), exist_ok=True)

    for var in ("contacts", "probes", "channels"):
        df = pd.DataFrame(metadata[var])
        drop_false_cols(df)
        df.to_csv(os.path.join(out_path, subject_id, session_id, "ephys", var + ".tsv"), sep="\t", index=False)


# Actually copy the NWB files

for nwb_file in nwb_files:
    nwb_file_bids_path = f"{out_path}/{metadata['subject']['subject_id']}/{metadata['session']['session_id']}/ephys/{metadata['subject']['subject_id']}_{metadata['session']['session_id']}.nwb"
    shutil.copyfile(nwb_file, nwb_file_bids_path)


