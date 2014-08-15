import requests
import argparse
import os
import sys

__base_url__ = "http://supfam3.cs.bris.ac.uk/FATHMM/"
__submit_url__ = __base_url__ + "cgi-bin/submit.cgi"
__result_url__ = __base_url__ + "cgi-bin/"
__download_url__ = __base_url__ + "tmp/"
__type__="CANCER" ##Hidden field to show which type of variants we are processing


def stop_err(msg, err=1):
    sys.stderr.write('%s\n' % msg)
    sys.exit(err)

def main_web(args):
    assert os.path.exists(args.input)
    with open(args.input) as f:
        contents = f.read().strip()
    threshold = -0.75
    if (args.threshold):
        threshold = args.threshold
    data = {"weighted": __type__,
            "batch": contents,
            "threshold": threshold
            }
    response = requests.post(__submit_url__, data=data)
    if response.status_code!=200:
        stop_err("Error processing request, got" + response.status_code)
    text = response.text
    split_text = text.split("window.location = ")
    try:
        url = split_text[1]
        url = url.split(";")[0]
        url = url.split("session=")[1]
        url = url.replace("'", "").replace("./","")
        url = __download_url__ + url + ".tab"
    except IndexError:
        stop_err("Unable to parse result id")
    print url
    response = requests.get(url)
    with open(args.output, 'wb') as fp:
        fp.write(response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process input output paths")
    parser.add_argument('--input',
                        type=str,
                        required=True,
                        help='Input file location')
    parser.add_argument('--output',
                        type=str,
                        required=True,
                        help='Output file location')
    parser.add_argument('--threshold',
                         type=float,
                         required=False,
                         help='Predictions with score less than threshold are possibly cancer causing')
    args = parser.parse_args()
    main_web(args)
