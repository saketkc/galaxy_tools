#!/usr/bin/python
from bs4 import BeautifulSoup
import argparse
import sys
import time
import os
import tempfile
import requests
import shutil
import csv
submission_url = 'http://genetics.bwh.harvard.edu/cgi-bin/ggi/ggi2.cgi'
result_url = 'http://genetics.bwh.harvard.edu'

TIMEOUT = 60 * 60 * 24
TIME_DELAY = 30
MAX_TRIES = 900000000

# Genome assembly version used for chromosome
# coordinates of the SNPs in user input
UCSCDB = ['hg19', 'hg18']
# Classifier model used for predictions.
MODELNAME = ['HumDiv', 'HumVar']

# Set of transcripts on which genomic SNPs will be mapped
SNPFILTER = {
    'All': 0,
    'Canonical': 1,
    'CCDS': 3,
}
# Functional SNP categories to include in genomic SNPs annotation report
SNPFUNCTION = ['c', 'm', '']


def stop_err(msg, err=1):
    sys.stderr.write('%s\n' % msg)
    sys.exit(err)


class Polyphen2Web:

    def __init__(self, ucscdb=None, model_name=None, snp_filter=None,
                 snp_function=None, file_location=None, email=None):
        self.ucscdb = ucscdb
        self.model_name = model_name
        self.snp_filter = snp_filter
        self.snp_function = snp_function
        self.file_location = file_location
        self.notify_me = email

    def soupify(self, string):
        return BeautifulSoup(string)

    def make_request(self):
        in_txt = csv.reader(open(self.file_location, 'rb'), delimiter='\t')
        tmp_dir = tempfile.mkdtemp()
        path = os.path.join(tmp_dir, 'csv_file')
        with open(path, 'wb') as fh:
            a = csv.writer(fh)
            a.writerows(in_txt)
        contents = open(self.file_location, 'r').read().replace(
            '\t', ' ').replace('::::::::::::::', '')
        if self.snp_function == 'All':
            self.snp_function = ''
        payload = {
            '_ggi_project': 'PPHWeb2',
            '_ggi_origin': 'query',
            '_ggi_batch': contents,
            '_ggi_target_pipeline': '1',
            'MODELNAME': self.model_name,
            'UCSCDB': self.ucscdb,
            'SNPFILTER': SNPFILTER[self.snp_filter],
            'SNPFUNC': self.snp_function,
            'NOTIFYME': '',

        }
        if self.notify_me:
            payload['NOTIFYME'] = self.notify_me
        request = requests.post(submission_url, data=payload)
        content = request.content
        soup = self.soupify(content)
        sid_soup = soup.find('input', {'name': 'sid'})
        try:
            sid = sid_soup['value']
        except:
            sid = None
        shutil.rmtree(tmp_dir)
        return sid

    def poll_for_files(self, sid,
                       max_tries=MAX_TRIES,
                       time_delay=TIME_DELAY,
                       timeout=TIMEOUT):
        payload = {
            '_ggi_project': 'PPHWeb2',
            '_ggi_origin': 'manage',
            '_ggi_target_manage': 'Refresh',
            'sid': sid,
        }
        content = None
        tries = 0
        url_dict = None
        while True:
            tries += 1
            if tries > max_tries:
                stop_err('Number of tries exceeded!')
            request = requests.post(submission_url, data=payload)
            content = request.content
            soup = self.soupify(content)
            all_tables = soup.findAll('table')
            if all_tables:
                try:
                    running_jobs_table = all_tables[-2]
                except:
                    running_jobs_table = None
                if running_jobs_table:
                    rows = running_jobs_table.findAll('tr')
                    if len(rows) == 1:
                        row = rows[0]
                        hrefs = row.findAll('a')
                        # print hrefs
                        if len(hrefs) >= 3:
                            short_txt = hrefs[0]['href']
                            # print short_txt
                            path = short_txt.split('-')[0]
                            full_txt = result_url + path + '-full.txt'
                            log_txt = result_url + path + '-log.txt'
                            snps_txt = result_url + path + '-snps.txt'
                            short_txt = result_url + path + \
                                '-short.txt'  # short_txt
                            url_dict = {
                                'full_file': full_txt,
                                'snps_file': snps_txt,
                                'log_file': log_txt,
                                'short_file': short_txt,
                            }
                            return url_dict
            time.sleep(time_delay)
        return url_dict

    def save_to_files(self, url_dict, args):
        tmp_dir = tempfile.mkdtemp()
        for key, value in url_dict.iteritems():
            r = requests.get(value, stream=True)
            if r.status_code == 200:
                path = os.path.join(tmp_dir, key)
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(128):
                        f.write(chunk)
                shutil.move(path, args[key])
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        return True


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-u',
                        '--ucscdb',
                        dest='ucscdb',
                        choices=UCSCDB,
                        required=True, type=str)
    parser.add_argument('-m', '--model',
                        dest='modelname', choices=MODELNAME,
                        required=True, type=str)
    parser.add_argument('-fl', '--filter',
                        '--snpfilter', dest='snpfilter',
                        choices=SNPFILTER.keys(),
                        required=True, type=str)
    parser.add_argument('-i', '--input',
                        dest='input', nargs='?',
                        required=True, type=str,
                        default=sys.stdin)
    parser.add_argument('-e', '--email',
                        dest='email',
                        required=False, default=None)
    parser.add_argument('--log', dest='log_file',
                        required=True, default=None, type=str)
    parser.add_argument('--short', dest='short_file',
                        required=True, default=None, type=str)
    parser.add_argument('--full', dest='full_file',
                        required=True, default=None, type=str)
    parser.add_argument('--snp', dest='snps_file',
                        required=True, default=None, type=str)
    parser.add_argument('--function', dest='snpfunction',
                        required=True, type=str)
    args_s = vars(parser.parse_args(args))
    polyphen2_web = Polyphen2Web(ucscdb=args_s['ucscdb'],
                                 model_name=args_s['modelname'],
                                 snp_filter=args_s['snpfilter'],
                                 snp_function=args_s['snpfunction'],
                                 file_location=args_s['input'],
                                 email=args_s['email'])
    sid = polyphen2_web.make_request()
    if not sid:
        stop_err(
            'Something went wrong! The tracking id could not be retrieved.')
    url_dict = polyphen2_web.poll_for_files(sid)
    locations = {}
    if not url_dict:
        stop_err('There was error downloading the output files!')
    for key in url_dict.keys():
        locations[key] = args_s[key]
    polyphen2_web.save_to_files(url_dict, locations)
    return True

if __name__ == '__main__':
    main(sys.argv[1:])
