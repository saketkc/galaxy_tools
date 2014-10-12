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


    def __init__(self, input_file):
        self.pending_urls = {}
        vcf_reader = vcf.Reader(open(input_file, 'r'))
        for record in vcf_reader:
            url = URL.format(record.CHROM, record.POS, record.POS, ("").join([str(x) for x in record.ALT]))
            key = "{}:{}-{}-{}".format(record.CHROM, record.POS, record.POS, ("").join([str(x) for x in record.ALT]))
            self.pending_urls[key] = url

    def submit(self):
        protein_variants = {}
        for key, url in self.pending_urls.iteritems():
            request = requests.get(url)
            time_delay = None
            try:
                retry_delay = request.headers['Retry-After']
                time_delay = retry_delay
            except KeyError:
                pass
            if time_delay:
                time.sleep(time_delay)
                request = requests.get(url)
            try:
                response = request.json()[0]
            except:
                #TODO Better error handling
                pass
            variants = response['transcript_consequences']
            for variant in variants:
                if 'protein_id' not in variant.keys() or 'protein_start' not in variant.keys():
                    continue
                if variant['protein_id'].startswith('ENSP'):
                    if variant['protein_id'] not in protein_variants.keys():
                        protein_variants[variant['protein_id']] = []
                    position = variant['protein_start']
                    try:
                        #TODO Better error handling
                        amino_acid_original, amino_acid_substituted = variant['amino_acids'].split("/")
                        substitution = amino_acid_original + str(position) + amino_acid_substituted
                        if not  "X" in substitution:
                            protein_variants[variant['protein_id']].append(substitution)
                    except:
                        pass
        for key, value in protein_variants.iteritems():
            if len(value)>0:
                print key, (",").join(value)






if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True, help="Input file location")
    args = parser.parse_args(sys.argv[1:])
    vep = VEPRestClient(args.input_file)
    vep.submit()

