import sys, re

def stop_err( msg ):
    sys.stderr.write( msg )
    sys.exit()

def __main__():
    try:
        infile =  open ( sys.argv[1], 'r')
        outfile = open ( sys.argv[2], 'w')
    except:
        stop_err( 'Cannot open or create a file\n' )

    if len( sys.argv ) < 5:
        stop_err( 'No columns to merge' )
    else:
        delimiter = sys.argv[3]
        cols = sys.argv[4:]

    skipped_lines = 0

    char_dict = {
        'T': '\t',
        's': '\s',
        'Dt': '\.',
        'Sl': '\\',
        'C': ',',
        'D': '-',
        'U': '_',
        'P': '\|',
        'Co': ':',
        'Sc': ';'
    }
    for line in infile:
        line = line.rstrip( '\r\n' )
        if line and not line.startswith( '#' ):
            fields = line.split( '\t' )
            line += '\t'
            for i, col in enumerate(cols):
                try:
                    if i!=len(cols)-1:
                        line += fields[ int( col ) -1 ] + char_dict[delimiter]
                    else:
                        line += fields[ int( col ) -1 ]

                except:
                    skipped_lines += 1

            print >>outfile, line

    if skipped_lines > 0:
        print 'Skipped %d invalid lines' % skipped_lines

if __name__ == "__main__" : __main__()
