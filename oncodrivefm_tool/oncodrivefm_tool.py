#!/usr/bin/python
import argparse
import sys
import os
import tempfile
import shutil
import subprocess
import ntpath

"""
 -h, --help            show this help message and exit
  -o PATH, --output-path PATH
                        Directory where output files will be written
  -n NAME               Analysis name
  --output-format FORMAT
                        The FORMAT for the output file
  -N NUMBER, --samplings NUMBER
                        Number of samplings to compute the FM bias pvalue
  -e ESTIMATOR, --estimator ESTIMATOR
                        Test estimator for computation.
  --gt THRESHOLD, --gene-threshold THRESHOLD
                        Minimum number of mutations per gene to compute the FM
                        bias
  --pt THRESHOLD, --pathway-threshold THRESHOLD
                        Minimum number of mutations per pathway to compute the
                        FM bias
  -s SLICES, --slices SLICES
                        Slices to process separated by commas
  -m PATH, --mapping PATH
                        File with mappings between genes and pathways to be
                        analysed
  --save-data           The input data matrix will be saved
  --save-analysis       The analysis results will be saved
  -j CORES, --cores CORES
                        Number of cores to use for calculations. Default is 0
                        that means all the available cores
  -D KEY=VALUE          Define external parameters to be saved in the results
  -L LEVEL, --log-level LEVEL
                        Define log level: debug, info, warn, error, critical,
                        notset
"""
def stop_err( msg ):
    sys.stderr.write( '%s\n' % msg )
    sys.exit()
def main(params):
    parser = argparse.ArgumentParser()
    ##TAKEN directly from the source code
    parser.add_argument("-N", "--samplings", dest="num_samplings", type=int, default=10000, metavar="NUMBER",
                                        help="Number of samplings to compute the FM bias pvalue")
    parser.add_argument("-e", "--estimator", dest="estimator", metavar="ESTIMATOR",
                                        choices=["mean", "median"], default="mean",
                                        help="Test estimator for computation.")
    parser.add_argument("--gt", "--gene-threshold", dest="mut_gene_threshold", type=int, default=2, metavar="THRESHOLD",
                                        help="Minimum number of mutations per gene to compute the FM bias")
    parser.add_argument("--pt", "--pathway-threshold", dest="mut_pathway_threshold", type=int, default=10, metavar="THRESHOLD",
                                        help="Minimum number of mutations per pathway to compute the FM bias")
    parser.add_argument("-s", "--slices", dest="slices", metavar="SLICES",
                                        help="Slices to process separated by commas")
    parser.add_argument("-m", "--mapping", dest="mapping", metavar="PATH",
                                        help="File with mappings between genes and pathways to be analysed")
    parser.add_argument("-f", "--filter", dest="filter", metavar="PATH",
                                        help="File containing the features to be filtered. By default labels are includes,"
                                                    " labels preceded with - are excludes.")
    #parser.add_argument("-o", "--output_path", type=str, required=True, help="Directory where output files will be written")
    parser.add_argument("-o1", "--output1", type=str, dest="output1", required=True)

    parser.add_argument("-o2", "--output2", type=str, dest="output2", required=False)
    parser.add_argument("-n", "--analysis_name", type=str, required=False, help="Analysis name")
    #parser.add_argument("-e", "--estimator", type=str, required=False, choices=["mean-empirical","median-empirical","mean-zscore","median-zscore"], help="Test estimator for computation")
    parser.add_argument("--output-format", dest="output_format", required=False,
                        metavar="FORMAT",
                        choices=["tsv", "tsv.gz", "tsv.bz2"],
                        default="tsv",
                        help="The FORMAT for the output file")
    parser.add_argument("-j", "--cores", dest="num_cores", type=int,
                        metavar="CORES",
                        help="Number of cores to use for calculations.\
                        Default is 0 that means all the available cores")
    parser.add_argument("-D", dest="defines", metavar="KEY=VALUE", action="append", help="Define external parameters to be saved in the results")
    parser.add_argument("-L", "--log-level", dest="log_level", metavar="LEVEL", default=None,
                        choices=["debug", "info", "warn", "error", "critical", "notset"],
                        help="Define log level: debug, info, warn, error, critical, notset")
    parser.add_argument("-i", "--input", dest="input_path", required=True, type=str, help="Path to input file")
    args = vars(parser.parse_args(params))
    try:
        mapping_path = args["mapping_path"]
    except KeyError:
        mapping_path = "no_mapping_path"
    #if mapping_path=="no_mapping_path":
        #params.remove(mapping_path)
        #params.remove("-m")
    output_dir = tempfile.mkdtemp()
    params.append("-o")
    params.append(output_dir)
    params.append(args["input_path"])
    cmd = "oncodrivefm "
    i=0
    while i<len(params):
        p=params[i]
        if p=="-i" or p=="-o1" or p=="-o2":
            i+=2
        else:
            i+=1
            cmd += " "+p
    cmd += " 2>&1 "
    #tmp = tempfile.NamedTemporaryFile( dir=output_dir ).name
    #tmp_stderr = open( tmp, 'wb' )
    print cmd
    proc = subprocess.Popen(args=cmd, shell=True)
    returncode = proc.wait()
    #tmp_stderr.close()

    if args['analysis_name'] is not None:
        prefix = args["analysis_name"]
    else:
        ##refer: http://stackoverflow.com/a/8384788/756986
        prefix = ntpath.basename(args["input_path"]).split(".")[0]
    if args["mapping"] is not None:
        pathway_file = prefix+"-pathways"
    else:
        pathway_file = None
    output_format = args["output_format"]
    genes_output_file_name = os.path.join(output_dir, prefix+"-genes."+output_format)
    shutil.move(genes_output_file_name,args["output1"])
    if pathway_file:
        pathway_output_file_name = os.path.join(output_dir, pathway_file+"."+output_format)
        shutil.move(pathway_output_file_name,args["output2"])
    if os.path.exists( output_dir ):
        shutil.rmtree( output_dir )
if __name__=="__main__":
    main(sys.argv[1:])
