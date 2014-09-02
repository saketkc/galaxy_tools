#!/usr/bin/env python
import sys
import argparse
import pandas

MAPPINGS={"ma": [ 8], "sift": [10,14], "polyphen" : []}
keys = ["sift", "ma", "polyphen"]

def stop_err(msg, err=1):
    sys.stderr.write('%s\n' % msg)
    sys.exit(err)


def main_web(args):
    if args[1]:
        print args[1]
        stop_err("Unknown parameters")
    var =  vars(args[0])
    params = [x for x in var if var[x]!=None]
    if len(params) < 2:
        stop_err("Need atleast two data to merge")
    data = {"ma_input": None, "sift_input": None, "polyphen_input": None}
    if var['sift_input']:
        data["sift_input"] = pandas.read_csv(var['sift_input'], delimiter='\t')[MAPPINGS["sift"]]
        #annotations = pandas.read_csv(var['sift_input'], delimiter='\t')[[1]]
    if var['ma_input']:
        annotations = pandas.read_csv(var['ma_input'], delimiter='\t')[[1]]
        data["ma_input"] = pandas.read_csv(var['ma_input'], delimiter='\t')[MAPPINGS["ma"]]
    if var["sift_input"] and var["ma_input"]:
        merge_df = data["sift_input"].join(data["ma_input"])
        merge_df.columns = ['Provean', 'Sift', 'MA' ]
        if var["polyphen_input"]:
            merge_df = merge_df.join(data["polyphen_input"])
            merge_df.columns = ['Provean', 'Sift', 'MA', 'Polyphen' ]

    if var["sift_input"] and var["polyphen_input"]:
        merge_df = var["sift_input"].join(var["ma_input"])
        merge_df.columns = ['Provean', 'Sift', 'Polyphen' ]
        if var["ma_input"]:
            merge_df = merge_df.join(data["ma_input"])
            merge_df.columns = ['Provean', 'Sift', 'Polyphen', 'MA' ]

    if var["ma_input"] and var["polyphen_input"]:
        merge_df = var["ma_input"].join(var["ma_input"])
        merge_df.columns = ['MA', 'Polyphen' ]
        if var["sift_input"]:
            merge_df = merge_df.join(data["sift_input"])
            merge_df.columns = ['Polyphen', 'MA', 'Provean', 'Sift']

    merge_df.insert(0, 'annotations', annotations)
    merge_df = merge_df.dropna()
    annotations = merge_df["annotations"]
    classes = pandas.Series([x.split(",")[1] for x in annotations])
    del(merge_df["annotations"])
    i = pandas.Series(merge_df.index)
    metadata_df = pandas.concat([i, classes], axis=1)
    if var["treat_binary"]:

        ##Set Damaging mutatiomn to true
        if var["sift_input"]:
            merge_df["Sift"] = merge_df["Sift"] <= var["sift_threshold"]
            merge_df["Provean"] = merge_df["Provean"] <= var["provean_threshold"]

        if var["polyphen_input"]:
            merge_df["Polyphen"] = merge_df["Sift"] >= var["polyphen_threshold"]

        if var["ma_input"]:
            merge_df["MA"] = merge_df["MA"] >= var["ma_threshold"]


        merge_df = merge_df.astype(int)
    merge_df.insert(0,'annotations', merge_df.index)
    metadata_df.columns =['annotations', 'class']
    merge_df.to_csv(var["output"], index=False)
    metadata_df.to_csv(var["metadata"], index=False)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process input output paths")
    parser.add_argument('--sift_input',
                        type=str,
                        help='Input file location')
    parser.add_argument('--sift_threshold',
                        type=float,
                        help='SIFT thresholdn')
    parser.add_argument('--provean_threshold',
                        type=float,
                        help='Provean thresholdn')
    parser.add_argument('--polyphen_input',
                        type=float,
                        help='Input file location')
    parser.add_argument('--polyphen_threshold',
                        type=float,
                        help='Provean thresholdn')
    parser.add_argument('--ma_input',
                        type=str,
                        help='Input file location')
    parser.add_argument('--ma_threshold',
                        type=float,
                        help='Input file location')
    parser.add_argument('--treat-binary', action='store_true')
    parser.add_argument('--metadata',
                        type=str,
                        help='Metadata file location')
    parser.add_argument('--output',
                        type=str,
                        help='Output file location')
    args = parser.parse_known_args()
    main_web(args)
