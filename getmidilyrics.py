#!/usr/bin/env python3

import  getopt
import  sys
import  os
import  signal
import  os.path
import  re

# Global variables

USAGESTR = """
Usage: %s  [-i <input_file>] [-l <lyrics_file>] [-m <marker_file>] [-h] [-d]

<input_file>    Text representation of MIDI file using perl::MIDI module
<lyrics_file>   Text file Lyrics, one per line
<marker_file>   Text dump of MIDI file with lyrics replaced by markers
"""
PROCESSPID  = os.getpid()
INPUTFILE   = None
LYRICSFILE  = "/tmp/lyrics_%d.txt" % PROCESSPID
MARKFILE    = "/tmp/markers_%d.txt" % PROCESSPID
DEBUG   = None
INPUTH  = None
LYRICSH = None
MARKH   = None

def usage( a_progname ):
    print(USAGESTR % a_progname)
### usage ###


def getArgs():
    global INPUTFILE, LYRICSFILE, MARKFILE, DEBUG
    optlist, _ = getopt.getopt(sys.argv[1:], 'i:hd' )
    for (arg, value) in optlist:
        if   arg == '-i':
            INPUTFILE = os.path.normpath(value)
        elif arg == '-h':
            usage( os.path.basename(sys.argv[0]) )
            exit(0)
        elif arg == '-d':
            DEBUG = 1
        else:
            pass
    ### for arg, filename
    if not INPUTFILE:
        print("Input file was not defined (use -i <input_file>)")
        exit(1)
    if not os.path.exists( INPUTFILE ):
        print(f"Input file '{INPUTFILE}' does not exit")
        exit(1) 
### parseArgs ###


def closeFiles():
    if INPUTH:
        INPUTH.close()
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
    global INPUTH, LYRICSH, MARKH, DEBUG
    # Based on input file create two more files
    # - Lyrics file (for editing)
    # - Placeholder file
    root, _ = os.path.splitext(INPUTFILE)
    LYRICSFILE = f"{root}.lyr.txt"
    MARKFILE = f"{root}.mark.txt"

    try:
        INPUTH = open( INPUTFILE, "r" )
        if DEBUG:
            print(f"Opened file '{INPUTFILE}'")
    except:
        print(f"Cannot open input file '{INPUTFILE}' for reading")
        exit(1)
    try:
        LYRICSH = open( LYRICSFILE, "w" )
    except:
        print(f"Cannot open file '{LYRICSFILE}' with lyrics only for writing")
        exit(1) 
    try:
        MARKH = open( MARKFILE, "w" )
    except: 
        print(f"Cannot open file '{MARKFILE}' with markers for writing")
        exit(1)
### openFiles ###


if __name__ == "__main__":
    handleSignals()
    getArgs()
    openFiles()

    LyrCount = 1
    
    TEXTREGEXP = r',\s[\'\"].+[\'\"]\],'
    CTRCHARREGEXP = r'\\x\w\w'
    
    CpldLyricRegExp = re.compile( TEXTREGEXP )
    CtrChrRegExp = re.compile( CTRCHARREGEXP )
    
    for InLine in INPUTH.readlines():
        if  InLine.find( "'lyric'" ) <= -1 and \
            InLine.find( "text_event'" ) <= -1 and \
            InLine.find( "'marker'" ) <= -1 and \
            InLine.find( "'track_name'" ) <= -1:
            MARKH.write( InLine )
            # \n not needed at the end, already exists
            continue
            
        # We found text- or lyric-event
        LyricReg = CpldLyricRegExp.search( InLine )
        if not LyricReg:
            #print "Hmmm, text event without text?!"
            #print "  " + InLine
            continue
        else:
            TextPlaceHolder = '#' + "%05d" % LyrCount + '#'
            EventText = LyricReg.group(0)[3:-3]
            # Text without start and end single- or double quote
            
            CtrChrReg = CtrChrRegExp.findall( EventText )
            if CtrChrReg:
                # Replace all control characters with their "numeric" replacements
                # All this is needed if user wants to transliterate karaoke
                # lyrics into Cyrillic letters, for example :-)
                for CtrChar in CtrChrReg:
                    NewCtrChar = '#%03d' % int( CtrChar[2:], 16 ) + '#'
                    EventText = EventText.replace( CtrChar, NewCtrChar )
                ### for CtrChar
                
            LYRICSH.write( TextPlaceHolder + "=\"" + EventText + "\"\n" )
            # Single quotes are needed so that editor notices spaces
            
            # Find start and end position of text event
            (StartPos,EndPos) = LyricReg.span()
            
            # See if there's apostrophe in line ... that one should be
            # "descaped" and appropriate lyric surrounded by ""
            if EventText.find( "'" ) > -1:
                #print EventText
                # Write text event to file
                LyricGroupStart = LyricReg.group(0)[:3]
                LyricGroupEnd = LyricReg.group(0)[-3:]
                LyricGroupStart = LyricGroupStart.replace( "'", '"', 1 ) # Replaced first '
                LyricGroupEnd = LyricGroupEnd.replace( "'", '"', 1 ) # Replace last '
                MARKH.write( InLine[:StartPos] + LyricGroupStart + TextPlaceHolder +
                    LyricGroupEnd + InLine[EndPos:] )
            else:
                # Write text event to file
                MARKH.write( InLine[:StartPos] + LyricReg.group(0)[:3] + TextPlaceHolder +
                    LyricReg.group(0)[-3:] + InLine[EndPos:] )
            LyrCount = LyrCount + 1
    ### for InLine ###
    
    closeFiles()

    if DEBUG:
        print(f"Exported lyrics from '{INPUTFILE}'")
        print(f"Put lyrics to lyrics file '{LYRICSFILE}'")
        print(f"Created marker file '{MARKFILE}'")

    exit(0)
