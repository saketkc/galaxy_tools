#!/usr/bin/env python
import sys
import requests
import os
import argparse
import re

__url__ = 'http://mutationassessor.org/'


def stop_err(msg, err=1):
    sys.stderr.write('%s\n' % msg)
    sys.exit(err)


def main_web(args):
    assert os.path.exists(args.input)
    with open(args.input) as f:
        contents = f.read().strip()
    if args.hg19 is True and args.protein is True:
        stop_err('--hg19 option conflicts with --protein')
    if args.protein is False:
        ## Replace tabs/space with commas
        re.sub('[\t\s]+', ',', contents)
    if args.hg19:
        ## Append hg19 to each line
        lines = contents.split('\n')
        contents = ('\n').join(
            map((lambda x: 'hg19,' + x),
                lines))

    payload = {'vars': contents, 'tableQ': 1}
    request = requests.post(__url__, data=payload)  # files=files)
    response = request.text
    if request.status_code != requests.codes.ok:
        stop_err("""Error retrieving response from server.
                 Server returned %s .
                 Output: %s
                 """ % (response.status_code, response.text))
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
                        help='Output file locatio')
    parser.add_argument('--log',
                        type=str,
                        required=False)
    parser.add_argument('--hg19',
                        action='store_true',
                        help="""Use hg19 build.
                        Appends 'hg19' to each input line""")
    parser.add_argument('--protein',
                        action='store_true',
                        help='Inputs are in protein space')
    args = parser.parse_args()
    main_web(args)
