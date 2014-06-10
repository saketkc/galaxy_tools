#!/usr/bin/env python
#By, Guruprasad Ananda.

import sys, re

def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()

def main():
    if len(sys.argv) != 5:
        stop_err("usage: convert_characters infile from_char to_char outfile")

    try:
        fin = open(sys.argv[1],'r')
    except:
        stop_err("Input file cannot be opened for reading.")

    from_char = sys.argv[2]
    to_char = sys.argv[3]

    try:
        fout = open(sys.argv[4],'w')
    except:
        stop_err("Output file cannot be opened for writing.")

    char_dict = {
        'T': '\t',
        's': '\s',
        'Dt': '\.',
        'C': ',',
        'D': '-',
        'U': '_',
        'P': '\|',
        'Co': ':',
        'Sc': ';'
    }
    from_ch = char_dict[from_char] + '+'    #making an RE to match 1 or more occurences.
    to_char = char_dict[to_char]
    skipped = 0

    for line in fin:
        line = line.strip()
        try:
            fout.write("%s\n" %(re.sub(from_ch, to_char, line)))
        except:
            skipped += 1

    fout.close()
    fin.close()
    if skipped:
        print "Skipped %d lines as invalid." %skipped

if __name__ == "__main__":
    main()
