#!/usr/bin/env python3

import itertools
import pathlib

import pandas as pd
import numpy as np
import scipy
import spikeinterface.full as si
import json
import csv
from scipy.io import loadmat
import neo

from bep032tools.generator.BEP032Generator import BEP032Data
from bep032tools.generator.utils import save_json, save_tsv

# b = BEP032Data()
# b.generate_metadata_file_channels()



class BIDSGenerator(BEP032Data):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.probe_name, self.probe_sources = self.load_probe_source_data()

    def generate_metadata_file_channels(self, output):

        recording_folder = self.custom_metadata_sources['source_data_folder']
        neo_reader = neo.get_io(recording_folder)
        # recording = si.NixRecordingExtractor(recording_folder, streamid)

        neo_streams = neo_reader.header['signal_streams']
        neo_channels = neo_reader.header['signal_channels']

        df = pd.DataFrame.from_records(neo_channels)
        df.rename(columns={'name': 'channel_id', 'id':'channel_name', 'sampling_rate':'sampling_frequency', 'units':'unit'}, inplace=True)
        df['type'] = 'EXT'

        # ensure all channels have a corresponding contact
        channel_contacts = df['channel_id'].str.extract(r'(\d+)').astype(int)
        assert all(np.isin(channel_contacts, self.probe_sources['chanMap0ind']))

        df.set_index('channel_id', inplace=True)

        save_tsv(df, output)

    def generate_metadata_file_probes(self, output): # get_probes_files(path):
        # only a single neuropixel probe used in this experiment
        df = pd.DataFrame(columns=['probe_id', 'type'], data=[[f'probe-{self.probe_name}', 'Neuropixel']])
        df.set_index('probe_id', inplace=True)
        save_tsv(df, output)

    def generate_metadata_file_contacts(self, output): #  get_contacts_files(probes_file):
        df = self.probe_sources.copy()

        df.rename(columns={'chanMap0ind':'contact_id','shankInd':'shank_id','chanMap':'1-indexed-contact_id', 'xcoords':'x','ycoords':'y'}, inplace=True)
        df.set_index('contact_id', inplace=True)

        save_tsv(df, output)

    def generate_metadata_file_dataset_description(self, output):
        mdict = {'author': ['Alice A', ' Bob B']}
        # Using a JSON string
        save_json(mdict, output)

    def generate_metadata_file_participants(self, output):
        df = pd.DataFrame(columns=['subject_id'], data=['sub-' + self.sub_id])
        df.set_index('subject_id', inplace=True)
        save_tsv(df, output)

    def generate_metadata_file_sessions(self, output):
        df = pd.DataFrame(columns=['session_id'], data=['ses-' + self.ses_id])
        df.set_index('session_id', inplace=True)
        save_tsv(df, output)

    def generate_metadata_file_ephys(self, output):
        mdict = {'PowerLineFrequency':60}
        save_json(mdict, output)

    def load_probe_source_data(self):
        sources_folder = self.custom_metadata_sources['source_data_folder'].parents[1]
        # Import .mat dataset
        mat_files = list(sources_folder.glob('*.mat'))
        #assert len(mat_files) == 1
        mat_file = mat_files[0]

        mat = scipy.io.loadmat(mat_file)
        df = pd.DataFrame()
        for key, values in mat.items():
            if key.startswith('__') or key == 'name':
                continue
            else:
                df[key] = values.flatten()

        if 'name' in mat:
            probe_name = mat['name'][0]
        else:
            probe_name = None

        return probe_name, df



if __name__ == '__main__':
    code_path = pathlib.Path(__file__).parent
    for sub_path in code_path.glob('../../sourcedata/sub-*'):
        print(f'Processing `{sub_path}`')
        sub_id = sub_path.name.split('sub-')[-1]
        for ses_path in sub_path.glob('ses-*'):
            ses_id = ses_path.name.split('ses-')[-1]

            gen = BIDSGenerator(sub_id, ses_id,
                                custom_metadata_source={'source_data_folder': ses_path})
            gen.basedir = code_path.parent
            gen.register_data_sources(ses_path)
            gen.generate_directory_structure()
            gen.organize_data_files(mode='link', autoconvert='nwb')
            gen.generate_all_metadata_files()



    # contacts_file = get_contacts_files(get_probes_files('neuropixPhase3A_kilosortChanMap.mat'))
    # channel_file = get_channel_file('/Users/killianrochet/Downloads/bep032-spikesorting-2/Cazette/dataset/sub-i/ses-123456/ephys/sub-i_ses-123456_task-r2g_run-001_ephys.nix',contacts_file)
    # print(contacts_file)
    # print(channel_file)

