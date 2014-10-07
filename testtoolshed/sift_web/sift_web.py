#!/usr/bin/env python
import requests
import argparse
import sys
from functools import wraps
import time
from bs4 import BeautifulSoup

__url__ = 'http://provean.jcvi.org/genome_prg_2.php'


def stop_err(msg, err=1):
    sys.stderr.write('%s\n' % msg)
    sys.exit(err)


def retry(ExceptionToCheck, tries=10, delay=3, backoff=2, logger=None):
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
                        # print msg
                        pass
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


class SIFTWeb:

    def __init__(self):
        self.full_download_url = 'http://provean.jcvi.org/serve_file.php?VAR=g%s/%s.result.tsv'
        self.condensed_download_url = 'http://provean.jcvi.org/serve_file.php?VAR=g%s/%s.result.one.tsv'
        self.summary_download_url = 'http://provean.jcvi.org/serve_file.php?VAR=g%s/%s.result.summary.tsv'
        self.url_dict = {'full': self.full_download_url,
                         'condensed': self.condensed_download_url,
                         'summary': self.summary_download_url}
        self.job_id = None

    def upload(self, inputpath):
        payload = {'table': 'human37_66'}
        in_txt = open(inputpath, 'rb').read()
        payload['CHR'] = in_txt
        request = requests.post( __url__, data=payload)#, files={'CHR_file': open(path)})
        return request.text

    @retry(requests.exceptions.HTTPError)
    def get_full_data(self, full_output):
        r = requests.request(
            'GET', (self.full_download_url) % (self.job_id, self.job_id))
        if r.text != 'No file exists':
            with open(full_output, 'wb') as f:
                f.write(r.text)
        else:
            raise(requests.HTTPError())

    @retry(requests.exceptions.HTTPError)
    def get_condensed_data(self, condensed_output):
        r = requests.request(
            'GET', (self.condensed_download_url) % (self.job_id, self.job_id))
        if r.text != 'No file exists':
            with open(condensed_output, 'wb') as f:
                f.write(r.text)
        else:
            raise(requests.HTTPError())

    @retry(requests.exceptions.HTTPError)
    def get_summary_data(self, summary_output):
        r = requests.request(
            'GET', (self.summary_download_url) % (self.job_id, self.job_id))
        if r.text != 'No file exists':
            with open(summary_output, 'wb') as f:
                f.write(r.text)
        else:
            raise(requests.HTTPError())


def main(params):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output1', type=str, required=True)
    parser.add_argument('--output2', type=str, required=True)
    parser.add_argument('--output3', type=str, required=True)
    args = parser.parse_args(params)
    sift_web = SIFTWeb()
    content = sift_web.upload(args.input)
    soup = BeautifulSoup(content)
    p = soup.findAll('p')
    job_id = p[1].string.split(':')[-1].replace(' ', '').replace(').', '')
    sift_web.job_id = job_id
    sift_web.get_full_data(args.output1)
    sift_web.get_condensed_data(args.output2)
    sift_web.get_summary_data(args.output3)


if __name__ == '__main__':
    main(sys.argv[1:])
