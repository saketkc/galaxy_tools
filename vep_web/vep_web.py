#!/usr/bin/env python
"""
Script to interact with Ensemble Variant Effect Predictor(VEP)
webservice
"""
import argparse
import requests
import sys


__submission_url__ = 'http://uswest.ensembl.org/{}/Tools/VEP/{}/Json/Tools/VEP/form_submit?db=core'
__core_choices__ = ['core', 'gencode_basic', 'refseq', 'merged']


class VEPSubmission:

    def __init__(self, args):
        self.specie = args.specie
        self.input_format = args.input_format
        self.input_file = args.input_file
        self.output_file = args.output
        self.core_type = args.core_type
        self.submission_url = __submission_url__.format(self.specie, self.specie)

    def submit(self):
        files = {'file': open(self.input_file, 'rb')}
        payload = {'species': self.specie,
                   'format': self.input_format,
                   'core_type': self.core_type}
        request = requests.post(self.submission_url, data=payload, files=files)
        print request.text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True, help="Input file location")
    parser.add_argument("--specie", type=str, required=True, help="Specie")
    parser.add_argument("--core_type", type=str, choices=__core_choices__)
    parser.add_argument("--input_format", type=str, required=True, help="Input format")
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args(sys.argv[1:])
    vep = VEPSubmission(args)
    vep.submit()

