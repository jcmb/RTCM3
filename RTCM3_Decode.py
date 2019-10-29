#!/usr/bin/env python

import sys
import argparse
from pprint import pprint
import re

import RTCM3
from RTCM3_Decls import *
import binascii
import string


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

CSG_Test=False
Looking_For_Frame=0
Looking_For_Data_Start=1
In_Data=2

if CSG_Test:
   RTCM_Frame_Line=re.compile(".*Receive RTCM v3 Frame Length (.+), Type (.+),")
   RTCM_Data_Single_Line=re.compile("RTCM v3 Data = \[(.*)\]")
   RTCM_Data_Line=re.compile("RTCM v3 Data = \[(.*)")
   RTCM_End_Data_Line=re.compile(" *(.*)\]")
   RTCM_State=Looking_For_Frame
   RTCM_Data=None


   for line in sys.stdin:
      line=line.rstrip()
#     print "line:",line
      """
      if RTCM_State == 0:
         print "Looking for Frame"
      elif RTCM_State == 1:
         print "Looking for Data Start"
      elif RTCM_State == 2:
         print "Looking for Data End"
      else:
         print "Error state", RTCM_State
      print "DATA", RTCM_Data
"""
      Regex = RTCM_Frame_Line.match(line) # Look for the start frame always

      if Regex:
#         print "Frame   Regex"
         RTCM_Frame_Type=int(Regex.group(2))
         rtcm3.packet_ID=RTCM_Frame_Type
         print "Frame   ", line
         RTCM_State=Looking_For_Data_Start
         RTCM_Data=None

      else:
         if RTCM_State==Looking_For_Data_Start:
            Regex = RTCM_Data_Single_Line.match(line)
            if Regex:
                  RTCM_Data=Regex.group(1)
                  RTCM_Data=string.replace(RTCM_Data," ","")
                  RTCM_Data=string.replace(RTCM_Data,"-","")
#                  print "Single RTCM Data, ", RTCM_Frame_Type, RTCM_Data
                  RTCM_Data=binascii.unhexlify(RTCM_Data)
                  RTCM_Data=bytearray(RTCM_Data)
   #               print "Frame   Regex"
   #               print "Frame   ", line
                  rtcm3.decode(RTCM_Frame_Type,RTCM_Data)
                  rtcm3.dump(dump_undecoded=Dump_Undecoded,dump_decoded=Dump_Decoded,dump_timestamp=Dump_TimeStamp);
                  RTCM_State=Looking_For_Frame
                  RTCM_Data=None

            else:
               Regex=RTCM_Data_Line.match(line)
               if Regex:
#                     print "Start of Data    ", line
                     RTCM_State=In_Data
                     RTCM_Data=Regex.group(1)
#                     print RTCM_Data
         else:
            if RTCM_State==In_Data:
               Regex=RTCM_End_Data_Line.match(line)
               if Regex:
#                     print "Found End ", line
                     RTCM_State=Looking_For_Frame
                     RTCM_Data+=" " + Regex.group(1)
                     RTCM_Data=string.replace(RTCM_Data," ","")
                     RTCM_Data=string.replace(RTCM_Data,"-","")
#                     print "End RTCM Data, ", RTCM_Data
                     RTCM_Data=binascii.unhexlify(RTCM_Data)
                     RTCM_Data=bytearray(RTCM_Data)
#                     print RTCM_Data

                     rtcm3.decode(RTCM_Frame_Type,RTCM_Data)
                     rtcm3.dump(dump_undecoded=Dump_Undecoded,dump_decoded=Dump_Decoded,dump_timestamp=Dump_TimeStamp);
                     RTCM_State=Looking_For_Frame
                     RTCM_Data=None

               else:
#                  print "In Data ", line
                  RTCM_Data+=" " + line.lstrip()
#                  print RTCM_Data

else:
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
                   print "Undecoded Data: " +ByteToHex(rtcm3.undecoded) + " Length (%)".format(len(rtcm3.undecoded));
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

