#!/usr/bin/env python
import requests
import pycurl
import os
from os.path import getsize
import argparse
import sys
import cStringIO
from functools import wraps
import tempfile
import shutil
import time

__url__ = "http://bg.upf.edu/transfic/taskService"


def stop_err(msg, err=1):
    sys.stderr.write('%s\n' % msg)
    sys.exit(err)


def retry(ExceptionToCheck, tries=12000000, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

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
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    #msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    msg = "Retrying in %d seconds..." % (mdelay)
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


class TransficUploader:

    def __init__(self):

        self.c = pycurl.Curl()
        self.c.setopt(pycurl.URL, __url__)
        self.c.setopt(pycurl.UPLOAD, 1)
        try:
            proxy = os.environ['http_proxy']
            self.c.setopt(pycurl.PROXY, proxy)
        except KeyError:
            pass
        self.c.setopt(pycurl.HTTPHEADER, ['Expect:'])
        self.c.setopt(pycurl.UPLOAD, 1)
        self.c.setopt(pycurl.NOPROGRESS, 1)
        self.c.setopt(pycurl.USERAGENT, "curl/7.27.0")
        self.c.setopt(pycurl.SSL_VERIFYPEER, 1)
        self.c.setopt(pycurl.CUSTOMREQUEST, "PUT")
        self.c.setopt(pycurl.TCP_NODELAY, 1)
        self.buf = cStringIO.StringIO()
        self.c.setopt(self.c.WRITEFUNCTION, self.buf.write)

    def upload_file(self, filepath):
        f = open(filepath)
        self.c.setopt(pycurl.INFILE, f)
        self.c.setopt(pycurl.INFILESIZE, getsize(filepath))

    def run(self):
        self.c.perform()

    def get_url(self):
        return self.buf.getvalue().strip()

    @retry(requests.exceptions.HTTPError)
    def result_exists(self, url):
        download_request = requests.request("GET", url)
        if download_request.status_code == 404 or download_request == 500:
            raise requests.HTTPError()
        elif "Task status is : error" in download_request.text:
            stop_err("No SNVs found!")
        else:
            return url

    @retry(requests.exceptions.HTTPError)
    def download_result(self, url, outpath):
        tmp_dir = tempfile.mkdtemp()
        r = requests.get(url, stream=True)
        if r.status_code == 500:
            raise requests.HTTPError()
        else:
            path = os.path.join(tmp_dir, "results.csv")
            with open(path, 'wb') as f:
                for chunk in r.iter_content(128):
                    f.write(chunk)
        shutil.move(path, outpath)
        shutil.rmtree(tmp_dir)


def main(params):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args(params)
    uploader = TransficUploader()
    uploader.upload_file(args.input)
    uploader.run()
    url = uploader.get_url()
    url = uploader.result_exists(url)
    uploader.download_result(url, args.output)


if __name__ == "__main__":
    main(sys.argv[1:])
