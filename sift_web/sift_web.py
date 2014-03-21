
import sys
sys.path.insert(0, '/home/saket/requests-new-urllib3-api/requests/packages/')
sys.path.insert(0, '/home/saket/requests-new-urllib3-api')


import requests
import argparse
import os,sys,csv
from functools import wraps
import tempfile, shutil,time
from bs4 import BeautifulSoup
__url__="http://provean.jcvi.org/genome_prg.php"
def stop_err( msg ):
    sys.stderr.write( '%s\n' % msg )
    sys.exit()

def retry(ExceptionToCheck, tries=10, delay=3, backoff=2, logger=None):

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
                    msg = "Retrying in %d seconds..." %  (mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        #print msg
                        pass
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
class SIFTWeb:
    def __init__(self):
        self.full_download_url = "http://provean.jcvi.org/serve_file.php?VAR=g%s/%s.result.tsv"
        self.condensed_download_url = "http://provean.jcvi.org/serve_file.php?VAR=g%s/%s.result.one.tsv"
        self.summary_download_url = "http://provean.jcvi.org/serve_file.php?VAR=g%s/%s.result.summary.tsv"
        self.url_dict={"full":self.full_download_url,"condensed":self.condensed_download_url,"summary":self.summary_download_url}

        pass
    def upload(self,inputpath):
        payload={"table":"human37_66"}
        tmp_dir = tempfile.mkdtemp()
        path = os.path.join(tmp_dir,"temp_file")
        in_txt = csv.reader(open(inputpath,"rb"), delimiter="\t")
        with open(path,"wb") as fp:
            out_csv = csv.writer(fp,delimiter=",")
            out_csv.writerows(in_txt)

        request = requests.post(__url__,data=payload,files={"CHR_file":open(path)})
        shutil.rmtree(tmp_dir)
        return request.text
    @retry(requests.exceptions.HTTPError)
    def get_full_data(self,job_id,full_output):
        r=requests.request("GET",(self.full_download_url)%(job_id,job_id))
        if r.text !="No file exists":
            with open(full_output,"wb") as f:
                f.write(r.text)
        else:
            return requests.HTTPError()

    @retry(requests.exceptions.HTTPError)
    def get_condensed_data(self,job_id,condensed_output):
        r=requests.request("GET",(self.condensed_download_url)%(job_id,job_id))
        if r.text !="No file exists":
            with open(condensed_output,"wb") as f:
                f.write(r.text)
        else:
            raise(requests.HTTPError())

    @retry(requests.exceptions.HTTPError)
    def get_summary_data(self,job_id,summary_output):
        r=requests.request("GET",(self.summary_download_url)%(job_id,job_id))
        if r.text !="No file exists":
            with open(summary_output,"wb") as f:
                f.write(r.text)
        else:
            raise(requests.HTTPError())
def main(params):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",type=str,required=True)
    parser.add_argument("--output1",type=str,required=True)
    parser.add_argument("--output2",type=str,required=True)
    parser.add_argument("--output3",type=str,required=True)

    args = parser.parse_args(params)
    sift_web = SIFTWeb()
    content=sift_web.upload(args.input)
    soup=BeautifulSoup(content)
    p = soup.findAll("p")
    job_id = p[1].string.split(":")[-1].replace(" ","").replace(").","")
    sift_web.get_full_data(job_id,args.output1)
    sift_web.get_condensed_data(job_id,args.output2)
    sift_web.get_summary_data(job_id,args.output3)
    #sift_web.save_data(args.output1,args.output2,args.output3)
if __name__=="__main__":
    main(sys.argv[1:])
