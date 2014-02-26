import rpy2.robjects as robjects
import argparse
import tempfile
import sys
import os
import shutil
import csv
from rpy2.robjects.packages import importr
tools = importr("utils")
import subprocess
def main(params):
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_input_file", type=str, required=True)
    parser.add_argument("--annotation_classes_file", type=str, required=True)
    parser.add_argument("--genelist_file", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args(params)
    raw_input_file = args.raw_input_file
    annotation_classes_file = args.annotation_classes_file
    genelist_file = args.genelist_file
    output = args.output

    tempdir = tempfile.mkdtemp()
    biplot_file = os.path.join(tempdir, "biplot")
    overview_file = os.path.join(tempdir, "overview")
    mappings = {}
    with open(annotation_classes_file,"rb") as input_file:
        reader = csv.reader(input_file, delimiter="\t", quotechar='"')
        next(reader, None)
        for row in reader:
            key = row[1]
            value = row[0]

            if key in mappings:
                mappings[key].append(value)
            else:
                mappings[key]=[value]
    keys = mappings.keys()
    robjects.globalenv['annotation_classes_file'] = annotation_classes_file
    robjects.globalenv['input_file'] = raw_input_file
    robjects.globalenv['genelist_file'] = genelist_file
    robjects.globalenv['overview_file'] = overview_file
    robjects.globalenv['biplot_file'] = biplot_file
    robjects.globalenv['control_columns']=robjects.StrVector(mappings[keys[0]])
    robjects.globalenv['disease_columns']=robjects.StrVector(mappings[keys[1]])
    robjects.r["Sweave"]("/home/saket/GALAXY/DDP-galaxy/tools/correpondence_analysis/correspondence_analysis.Rnw")
    #DEVNULL = open(os.devnull, 'wb')
    #subprocess.Popen()
    #robjects.r["texi2dvi"]("/home/saket/GALAXY/DDP-galaxy/tools/correpondence_analysis/correspondence_analysis.tex", clean=True, quiet=True, pdf=True)
    #return True
    os.chdir("/home/saket/GALAXY/DDP-galaxy/tools/correpondence_analysis/")
    process = subprocess.call(["pdflatex", "/home/saket/GALAXY/DDP-galaxy/tools/correpondence_analysis/correspondence_analysis.tex"], shell=False)
    #DEVNULL.close()


    #print tempdir


    shutil.move("/home/saket/GALAXY/DDP-galaxy/tools/correpondence_analysis/correspondence_analysis.pdf",output)
    shutil.rmtree(tempdir)

if __name__ == "__main__":
    main(sys.argv[1:])

