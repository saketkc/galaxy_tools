#!/usr/bin/python
"""
The MIT License (MIT)

Copyright (c) 2014 Saket Choudhary, <saketkc@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import sys
import requests
import argparse
import time
from functools import wraps
import json
import zipfile
import tempfile
import ntpath
import shutil
import xlrd
import csv
import os
sheet_map = {0: 'Variant_Analysis.csv',
             1: 'Amino_Acid_Level_Analysis.csv', 2: 'Gene_Level_Analysis.csv'}


def retry(ExceptionToCheck, tries=40000, delay=3, backoff=2, logger=None):
    '''Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    '''
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    #msg = '%s, Retrying in %d seconds...' % (str(e), mdelay)
                    msg = 'Retrying in %d seconds...' % (mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
CANCERTYPES = ['Bladder', 'Blood-Lymphocyte', 'Blood-Myeloid',
               'Brain-Cerebellum', 'Brain-Glioblastoma_Multiforme',
               'Brain-Lower_Grade_Glioma', 'Breast', 'Cervix',
               'Colon', 'Head_and_Neck', 'Kidney-Chromophobe',
               'Kidney-Clear_Cell', 'Kidney-Papiallary_Cell',
               'Liver-Nonviral', 'Liver-Viral', 'Lung-Adenocarcinoma',
               'Lung-Squamous_Cell', 'Melanoma', 'Other', 'Ovary',
               'Pancreas', 'Prostate-Adenocarcinoma', 'Rectum',
               'Skin', 'Stomach', 'Thyroid', 'Uterus']

__URL__ = 'http://www.cravat.us/rest/service/submit'


def stop_err(msg):
    sys.stderr.write('%s\n' % msg)
    sys.exit()


class CHASMWeb:

    def __init__(self,
                 mutationbox=None, filepath=None,
                 is_hg_18=None, analysis_type=None,
                 analysis_program=None, chosendb=None,
                 cancer_type=None, email=None,
                 annotate_genes=None, text_reports=None,
                 mupit_out=None):
        self.mutationbox = mutationbox
        self.filepath = filepath
        self.is_hg_18 = is_hg_18
        self.analysis_type = analysis_type
        self.analysis_program = analysis_program
        self.chosendb = chosendb
        self.email = email
        self.annotate_genes = annotate_genes
        self.cancer_type = cancer_type
        self.email = email
        self.annotate_genes = annotate_genes
        self.text_reports = text_reports
        self.mupit_input = mupit_out

    def make_request(self):
        data = {
            'mutations  ': self.mutationbox,
            'hg18': self.is_hg_18,
            'analysistype': self.analysis_type,
            'analysisitem': self.analysis_program,
            'chasmclassifier': self.cancer_type,
            'geneannotation': self.annotate_genes,
            'email': self.email,
            'tsvreport': 'on',  # self.text_reports,
            'mupitinput': self.mupit_input,
        }
        stripped_data = {}

        for key, value in data.iteritems():
            if value is True:
                value = 'on'
            if value is not None and value is not False:
                stripped_data[key] = value

        if not self.mutationbox:
            file_payload = {'inputfile': open(self.filepath)}
            request = requests.post(
                __URL__, data=stripped_data, files=file_payload)
        else:
            request = requests.post(
                __URL__, data=stripped_data, files=dict(foo='bar'))
        print request.text
        job_id = json.loads(request.text)['jobid']
        return job_id

    @retry(requests.exceptions.HTTPError)
    def zip_exists(self, job_id):
        print job_id
        url = 'http://www.cravat.us/results/%s/%s.zip' % (job_id, job_id)
        zip_download_request = requests.request('GET', url)
        if zip_download_request.status_code == 404:
            raise requests.HTTPError()
        else:
            return url

    def download_zip(self, url, job_id):
        self.tmp_dir = tempfile.mkdtemp()
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            self.path = os.path.join(self.tmp_dir, job_id + '.zip')
            with open(self.path, 'wb') as f:
                for chunk in r.iter_content(128):
                    f.write(chunk)
        else:
            self.path = None
        return self.path

    def move_files(self, file_map):
        fh = open(self.path, 'rb')
        zip_files = zipfile.ZipFile(fh)
        for name in zip_files.namelist():
            filename = ntpath.basename(name)
            extension = ntpath.splitext(filename)[-1]
            source_file = zip_files.open(name)
            if extension == '.txt':
                target_file = open(file_map['error.txt'], 'wb')
            elif filename != 'SnvGet Feature Description.xls' and extension != '.xls':
                target_file = open(file_map[filename], 'wbb')
            else:
                target_file = None
            if target_file:
                with source_file, target_file:
                    shutil.copyfileobj(source_file, target_file)
            if filename == 'SnvGet Feature Description.xls':
                with xlrd.open_workbook(source_file) as wb:
                    sheet_names = wb.sheet_names()
                    for name in sheet_names:
                        sh = wb.sheet_by_name(name)
                        name_shortened = name.replace(' ').strip() + '.csv'
                        with open(name_shortened, 'wb') as f:
                            c = csv.writer(f)
                            for r in range(sh.nrows):
                                c.writerow(sh.row_values(r))
        shutil.rmtree(self.tmp_dir)
        fh.close()


def main(params):

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        type=str, dest='mutationbox',
                        help='Input variants')
    parser.add_argument('--path', type=str,
                        dest='input_file_location',
                        help='Input file location')
    parser.add_argument('--hg18', dest='hg18',
                        action='store_true')
    parser.add_argument('--analysis_type', dest='analysis_type',
                        type=str,
                        choices=['driver', 'functional',
                                 'geneannotationonly'],
                        default='driver')
    parser.add_argument('--chosendb', dest='chosendb',
                        type=str, nargs='*',
                        choices=['CHASM', 'SnvGet'],
                        default='CHASM')
    parser.add_argument('--cancertype', dest='cancer_type',
                        type=str, choices=CANCERTYPES,
                        required=True)
    parser.add_argument('--email', dest='email',
                        required=True, type=str)
    parser.add_argument('--annotate', dest='annotate',
                        action='store_true', default=None)
    parser.add_argument('--tsv_report', dest='tsv_report',
                        action='store_true', default=None)
    parser.add_argument('--mupit_out', dest='mupit_out',
                        action='store_true', default=None)
    parser.add_argument('--gene_analysis_out', dest='gene_analysis_out',
                        type=str, required=True)
    parser.add_argument('--variant_analysis_out',
                        dest='variant_analysis_out',
                        type=str, required=True)
    parser.add_argument('--amino_acid_level_analysis_out',
                        dest='amino_acid_level_analysis_out',
                        type=str, required=True,)
    parser.add_argument('--codon_level_analysis_out',
                        dest='codon_level_analysis_out',
                        type=str, required=True,)
    parser.add_argument('--error_file', dest='error_file_out',
                        type=str, required=True)
    parser.add_argument('--snv_box_out', dest='snv_box_out',
                        type=str, required=False)
    parser.add_argument('--snv_features', dest='snv_features_out',
                        type=str, required=False)
    args = parser.parse_args(params)
    chasm_web = CHASMWeb(mutationbox=args.mutationbox,
                         filepath=args.input_file_location,
                         is_hg_18=args.hg18,
                         analysis_type=args.analysis_type,
                         chosendb=args.chosendb,
                         cancer_type=args.cancer_type,
                         email=args.email,
                         annotate_genes=args.annotate,
                         text_reports=args.tsv_report,
                         mupit_out=args.mupit_out)
    job_id = chasm_web.make_request()
    file_map = {'Amino_Acid_Level_Analysis.Result.tsv': args.amino_acid_level_analysis_out,
                'SNVBox.tsv': args.snv_box_out,
                'Variant_Analysis.Result.tsv': args.variant_analysis_out,
                'Gene_Level_Analysis.Result.tsv': args.gene_analysis_out,
                'SnvGet Feature Description.xls': args.snv_features_out,
                'error.txt': args.error_file_out,
                'Codon_Level_Analysis.Result.tsv': args.codon_level_analysis_out,
                }
    url = chasm_web.zip_exists(job_id)
    download = chasm_web.download_zip(url, job_id)
    if download:
        chasm_web.move_files(file_map=file_map)
    else:
        stop_err('Unable to download from the server')

if __name__ == '__main__':
    main(sys.argv[1:])
