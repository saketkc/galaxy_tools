#!/usr/bin/env python
"""
Script to interact with Ensemble Variant Effect Predictor(VEP)
webservice


The MIT License (MIT)

Copyright (c) 2014  Saket Choudhary<saketkc@gmail.com, skchoudh@usc.edu>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import argparse
import requests
import sys
import time
import vcf

URL = 'http://grch37.rest.ensembl.org/vep/human/region/{}:{}-{}/{}?content-type=application/json&protein=1'

class VEPRestClient:

    def __init__(self, input_file, output_file):
        self.pending_urls = []
        vcf_reader = vcf.Reader(open(input_file, 'r'))
        self.output_file = output_file
        for record in vcf_reader:
            url = URL.format(record.CHROM, record.POS, record.POS, ("").join([str(x) for x in record.ALT]))
            key = "{}:{}-{}-{}".format(record.CHROM, record.POS, record.POS, ("").join([str(x) for x in record.ALT]))
            self.pending_urls.append((key, url))

    def submit(self):
        protein_variants = {}
        for record in self.pending_urls:
            vcf_key = record[0]
            url = record[1]
            request = requests.get(url)
            time_delay = None
            try:
                retry_delay = request.headers['Retry-After']
                time_delay = retry_delay
            except KeyError:
                pass
            response = None
            if time_delay:
                time.sleep(time_delay)
                request = requests.get(url)
            try:
                response = request.json()[0]
            except Exception as e:
                #TODO Better error handling
                print e
            if not response:
                continue
            variants = response['transcript_consequences']
            consequence = ""
            for variant in variants:
                consequence  = ""
                protein_id = None
                protein_start = None
                try:
                    protein_id  = variant['protein_id']
                except KeyError:
                    pass
                try:
                    protein_start = variant['protein_start']
                except KeyError:
                    pass
                if protein_id:
                    if protein_id.startswith('ENSP'):
                        if variant['protein_id'] not in protein_variants.keys():
                            protein_variants[protein_id] = []
                            consequence += protein_id
                        if protein_start:
                            try:
                                #TODO Better error handling
                                amino_acid_original, amino_acid_substituted = variant['amino_acids'].split("/")
                                substitution = amino_acid_original + str(protein_start) + amino_acid_substituted
                                if "X" not  in substitution:
                                    protein_variants[variant['protein_id']].append(substitution)
                                    consequence += "  ," + substitution
                            except:
                                pass

        output = ""
        for key, value in protein_variants.iteritems():
            if len(value)>0:
                output += "{}   {}\n".format(key, (",").join(value))

        with open(self.output_file, 'wb') as f:
            f.write(output)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True, help="Input file location")
    parser.add_argument("--output_file", type=str, required=True, help="Output file location")
    args = parser.parse_args(sys.argv[1:])
    vep = VEPRestClient(args.input_file, args.output_file)
    vep.submit()

