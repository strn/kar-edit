#!/usr/bin/env python3

import  getopt
import  sys
import  os
import  signal
import  os.path
import  re

# Global variables

USAGESTR = """
Usage: %s  [-o <output_file>] [-l <lyrics_file>] [-m <marker_file>] [-h] [-d]

<output_file>   Text representation of MIDI file using perl::MIDI module
<lyrics_file>   Text file with lyrics, one per line
<marker_file>   Text dump of MIDI file with lyrics replaced by markers
"""
PROCESSPID  = os.getpid()
OUTPUTFILE   = None
LYRICSFILE  = "/tmp/merge_lyrics_%d.txt" % PROCESSPID
MARKFILE    = "/tmp/merge_markers_%d.txt" % PROCESSPID
DEBUG   = None
OUTPUTH = None
LYRICSH = None
MARKH   = None
LYRICS  = {} # Hash table for keeping lyrics

def usage( a_progname ):
    print(USAGESTR % a_progname)
### usage ###


def getArgs():
    global INPUTFILE, LYRICSFILE, MARKFILE, DEBUG
    optlist, _ = getopt.getopt(sys.argv[1:], 'i:hd')
    for (arg, value) in optlist:
        if   arg == '-i':
            INPUTFILE = os.path.normpath(value)
        elif arg == '-h':
            usage(os.path.basename(sys.argv[0]))
            exit(0)
        elif arg == '-d':
            DEBUG = 1
        else:
            pass
    ### for arg, filename
    if not INPUTFILE:
        print("Input file was not defined (use -i <input_file>)")
        exit(1)
### parseArgs ###


def closeFiles():
    if OUTPUTH:
        OUTPUTH.close()
    if LYRICSH:
        LYRICSH.close()
    if MARKH:
        MARKH.close()
### closeFiles ###


def handleSIGSTOP( aSigNum, aFrame ):
    closeFiles()
    rmTempFiles()
### handleSIG ###


def handleSIGCONT( aSigNum, aFrame ):
    pass
### handleSIG ###


def handleSIGINT( aSigNum, aFrame ):
    closeFiles()
    rmTempFiles()
### handleSIG ###
 
    
def handleSIGUSR1( aSigNum, aFrame ):
    pass
### handleSIG ###


def handleSIGUSR2( aSigNum, aFrame ):
    pass
### handleSIG ###

    
def handleSignals():
    signal.signal(signal.SIGTSTP, handleSIGSTOP)
    signal.signal(signal.SIGCONT, handleSIGCONT)
    signal.signal(signal.SIGINT,  handleSIGINT)
    signal.signal(signal.SIGUSR1, handleSIGUSR1)
    signal.signal(signal.SIGUSR2, handleSIGUSR2)
### handleSignals ###


def rmTempFiles():
    global DEBUG
    if DEBUG:
        # TODO
        print("Removing temporary files ...")
### rmTempFiles ###


def openFiles():
    global OUTPUTFILE, OUTPUTH, LYRICSH, MARKH, DEBUG
    # Based on input file read two files
    # - Lyrics file (for editing)
    # - Placeholder file
    # and create output file

    root, _ = os.path.splitext(INPUTFILE)
    LYRICSFILE = f"{root}.lyr.txt"
    MARKFILE = f"{root}.mark.txt"
    OUTPUTFILE = f"{root}.edit.txt"

    try:
        OUTPUTH = open( OUTPUTFILE, "w" )
        if DEBUG:
            print("Opened file '%s'" % OUTPUTFILE)
    except:
        print("Cannot open output file %s for writing" % OUTPUTFILE)
        exit(1)
        
    try:
        LYRICSH = open( LYRICSFILE, "r" )
    except:
        print("Cannot open file %s with lyrics only for reading" % LYRICSFILE)
        exit(1)
        
    try:
        MARKH = open( MARKFILE, "r" )
    except: 
        print("Cannot open file '%s' with markers for reading" % MARKFILE)
        exit(1)
### openFiles ###


if __name__ == "__main__":
    handleSignals()
    getArgs()
    openFiles()

    LyrCount = 1
    
    TEXTREGEXP = r'#\d{5}#'
    CTRCHARREGEXP = r'#\d{3}#'
    
    LyricMarkRegExp = re.compile( TEXTREGEXP )
    CtrChrMarkRegExp = re.compile( CTRCHARREGEXP )
    
    # Read translated/corrected/edited lyrics from lyrics file
    for InLine in LYRICSH.readlines():
        InLine = InLine.strip()
        LyricMark,LyricText = InLine.split( '=' )
        LYRICS[ LyricMark.strip() ] = LyricText.strip( '"' )
    ### for InLine ###
    
    for InLine in MARKH.readlines():
        LyricReg = LyricMarkRegExp.search( InLine )
        if not LyricReg:
            OUTPUTH.write( InLine )
            continue
        # Find marker
        MarkerText = LyricReg.group(0)
        (StartPos, EndPos) = LyricReg.span()
        
        if MarkerText in LYRICS:
            LyricsText = LYRICS[ MarkerText ]
            # Replace all control characters in format #000#
            CtrChrReg = CtrChrMarkRegExp.findall( LyricsText )
            if CtrChrReg:
                for CtrChar in CtrChrReg:
                    HexCtrChar = '\\x%02x' % int( CtrChar[1:-1] )
                    LyricsText = LyricsText.replace( CtrChar, HexCtrChar )
                ### for CtrChar ###
            OUTPUTH.write( InLine[:StartPos] + LyricsText + InLine[EndPos:] )
        else:
            # do not put anything
            OUTPUTH.write( InLine[:StartPos] + InLine[EndPos:] )
    ### for InLine ###
    
    closeFiles()

    if DEBUG:
        print(f"Reading markers from '{MARKFILE}' file")
        print(f"Reading lyrics from '{LYRICSFILE}' file")
        print(f"Writing lyrics to '{OUTPUTFILE}' file ")

    exit(0)
