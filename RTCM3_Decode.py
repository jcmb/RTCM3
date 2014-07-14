#!/usr/bin/env python

import sys
import argparse
import pprint

import RTCM3
from RTCM3_Decls import *


# ByteToHex From http://code.activestate.com/recipes/510399-byte-to-hex-and-hex-to-byte-string-conversion/

def ByteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    hex = []
    for aChar in byteStr:
        hex.append( "%02X " % aChar )

    return ''.join( hex ).strip()

class ArgParser(argparse.ArgumentParser):

    def convert_arg_line_to_args(self, arg_line):
        for arg in arg_line.split():
            if not arg.strip():
                continue
            yield arg


parser = ArgParser(
            description='RTCM  V3 packet decoder',
            fromfile_prefix_chars='@',
            epilog="(c) JCMBsoft 2013")

parser.add_argument("-U", "--Undecoded", action="store_true", help="Displays Undecoded Packets")
parser.add_argument("-D", "--Decoded", action="store_true", help="Displays Decoded Packets")
parser.add_argument("-L", "--Level", type=int, help="Output level, how much detail will be displayed. Default=2", default=2, choices=[0,1,2,3,4])
parser.add_argument("-N", "--None", nargs='+', help="Packets that should not be dumped")
parser.add_argument("-I", "--ID", nargs='+', help="Packets that should have there ID dumped only")
parser.add_argument("-S", "--Summary", nargs='+', help="Packets that should have a Summary dumped")
parser.add_argument("-F", "--Full", nargs='+', help="Packets that should be dumped Fully")
parser.add_argument("-V", "--Verbose", nargs='+', help="Packets that should be dumped Verbosely")
parser.add_argument("-E", "--Explain", action="store_true", help="System Should Explain what is is doing, AKA Verbose")
parser.add_argument("-W", "--Time", action="store_true", help="Report the time when the packet was received")

args=parser.parse_args()

#print args

Dump_Undecoded = args.Undecoded
Dump_Decoded = args.Decoded
Dump_TimeStamp = args.Time

rtcm3=RTCM3.RTCM3(default_output_level=args.Level);


if args.Explain:
    print "Dump undecoded: {},  Dump Decoded: {}, Dump TimeStamp: {}".format(
        Dump_Undecoded,
        Dump_Decoded,
        Print_ACK_NAK,
        Dump_TimeStamp)

if args.None:
    for id in args.None:
        if args.Explain:
            print "Decode Level None: " + hex(int(id,0))
        rtcm3.Dump_Levels[int(id,0)]=Dump_None

if args.ID:
    for id in args.ID:
        if args.Explain:
            print "Decode Level ID: " + hex(int(id,0))
        rtcm3.Dump_Levels[int(id,0)]=Dump_ID

if args.Summary:
    for id in args.Summary:
        if args.Explain:
            print "Decode Level Summary: " + hex(int(id,0))
        rtcm3.Dump_Levels[int(id,0)]=Dump_Summary

if args.Full:
    for id in args.Full:
        if args.Explain:
            print "Decode Level Full: " + hex(int(id,0))
        rtcm3.Dump_Levels[int(id,0)]=Dump_Full

if args.Verbose:
    for id in args.Verbose:
        if args.Explain:
            print "Decode Level Verbose: " + hex(int(id,0))
        rtcm3.Dump_Levels[int(id,0)]=Dump_Verbose



#input_file=open ('RTCM3.bin','rb')
#new_data = bytearray(input_file.read(255))
new_data = bytearray(sys.stdin.read(1))
while (new_data):

    rtcm3.add_data (data=new_data)
#    new_data=""
    if len(rtcm3.buffer):
#        print str(len(rtcm3.buffer))
        sys.stdout.flush()
    result = rtcm3.process_data (dump_decoded=False)
    while result != 0 :
#        print str(datetime.now())
        if result == Got_Undecoded :
            if Dump_Undecoded :
                print "Undecoded Data: " +ByteToHex(rtcm3.undecoded);
        elif result == Got_Packet :
            rtcm3.dump(dump_undecoded=Dump_Undecoded,dump_decoded=Dump_Decoded,dump_timestamp=Dump_TimeStamp);
            sys.stdout.flush()
        else :
                print "INTERNAL ERROR: Unknown result (" + str (result) + ")";
                sys.exit();
#        print "processing"
        result = rtcm3.process_data ()
#        print "processed: " + str(result)
    new_data = sys.stdin.read(1)
#    new_data = input_file.read(255)

print "Bye"

