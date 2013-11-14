#!/usr/bin/env python

from array import array
from RTCM3_Decls import *
import glob
import RTCM3_Definition
import sys
import pprint
from datetime import datetime

RTCM3_Preamble = 0xD3;
RTCM3_Max_Data_Length = 1023;
RTCM3_First_Data_Location = 3 # Zero based
RTCM3_Min_Size       = 6;
RTCM3_Max_Data_Length = 1023;
RTCM3_Max_Message_Length = RTCM3_Min_Size + RTCM3_Max_Data_Length;
RTCM3_Length_Location = 1 # Zero Based


#(*****************************************************************/
#/*                     CRC24 LOOKUP TABLE                        */
#/*****************************************************************)
crc24table =  (
 0x000000, 0x864CFB, 0x8AD50D, 0x0C99F6, 0x93E6E1, 0x15AA1A,
 0x1933EC, 0x9F7F17, 0xA18139, 0x27CDC2, 0x2B5434, 0xAD18CF,
 0x3267D8, 0xB42B23, 0xB8B2D5, 0x3EFE2E, 0xC54E89, 0x430272,
 0x4F9B84, 0xC9D77F, 0x56A868, 0xD0E493, 0xDC7D65, 0x5A319E,
 0x64CFB0, 0xE2834B, 0xEE1ABD, 0x685646, 0xF72951, 0x7165AA,
 0x7DFC5C, 0xFBB0A7, 0x0CD1E9, 0x8A9D12, 0x8604E4, 0x00481F,
 0x9F3708, 0x197BF3, 0x15E205, 0x93AEFE, 0xAD50D0, 0x2B1C2B,
 0x2785DD, 0xA1C926, 0x3EB631, 0xB8FACA, 0xB4633C, 0x322FC7,
 0xC99F60, 0x4FD39B, 0x434A6D, 0xC50696, 0x5A7981, 0xDC357A,
 0xD0AC8C, 0x56E077, 0x681E59, 0xEE52A2, 0xE2CB54, 0x6487AF,
 0xFBF8B8, 0x7DB443, 0x712DB5, 0xF7614E, 0x19A3D2, 0x9FEF29,
 0x9376DF, 0x153A24, 0x8A4533, 0x0C09C8, 0x00903E, 0x86DCC5,
 0xB822EB, 0x3E6E10, 0x32F7E6, 0xB4BB1D, 0x2BC40A, 0xAD88F1,
 0xA11107, 0x275DFC, 0xDCED5B, 0x5AA1A0, 0x563856, 0xD074AD,
 0x4F0BBA, 0xC94741, 0xC5DEB7, 0x43924C, 0x7D6C62, 0xFB2099,
 0xF7B96F, 0x71F594, 0xEE8A83, 0x68C678, 0x645F8E, 0xE21375,
 0x15723B, 0x933EC0, 0x9FA736, 0x19EBCD, 0x8694DA, 0x00D821,
 0x0C41D7, 0x8A0D2C, 0xB4F302, 0x32BFF9, 0x3E260F, 0xB86AF4,
 0x2715E3, 0xA15918, 0xADC0EE, 0x2B8C15, 0xD03CB2, 0x567049,
 0x5AE9BF, 0xDCA544, 0x43DA53, 0xC596A8, 0xC90F5E, 0x4F43A5,
 0x71BD8B, 0xF7F170, 0xFB6886, 0x7D247D, 0xE25B6A, 0x641791,
 0x688E67, 0xEEC29C, 0x3347A4, 0xB50B5F, 0xB992A9, 0x3FDE52,
 0xA0A145, 0x26EDBE, 0x2A7448, 0xAC38B3, 0x92C69D, 0x148A66,
 0x181390, 0x9E5F6B, 0x01207C, 0x876C87, 0x8BF571, 0x0DB98A,
 0xF6092D, 0x7045D6, 0x7CDC20, 0xFA90DB, 0x65EFCC, 0xE3A337,
 0xEF3AC1, 0x69763A, 0x578814, 0xD1C4EF, 0xDD5D19, 0x5B11E2,
 0xC46EF5, 0x42220E, 0x4EBBF8, 0xC8F703, 0x3F964D, 0xB9DAB6,
 0xB54340, 0x330FBB, 0xAC70AC, 0x2A3C57, 0x26A5A1, 0xA0E95A,
 0x9E1774, 0x185B8F, 0x14C279, 0x928E82, 0x0DF195, 0x8BBD6E,
 0x872498, 0x016863, 0xFAD8C4, 0x7C943F, 0x700DC9, 0xF64132,
 0x693E25, 0xEF72DE, 0xE3EB28, 0x65A7D3, 0x5B59FD, 0xDD1506,
 0xD18CF0, 0x57C00B, 0xC8BF1C, 0x4EF3E7, 0x426A11, 0xC426EA,
 0x2AE476, 0xACA88D, 0xA0317B, 0x267D80, 0xB90297, 0x3F4E6C,
 0x33D79A, 0xB59B61, 0x8B654F, 0x0D29B4, 0x01B042, 0x87FCB9,
 0x1883AE, 0x9ECF55, 0x9256A3, 0x141A58, 0xEFAAFF, 0x69E604,
 0x657FF2, 0xE33309, 0x7C4C1E, 0xFA00E5, 0xF69913, 0x70D5E8,
 0x4E2BC6, 0xC8673D, 0xC4FECB, 0x42B230, 0xDDCD27, 0x5B81DC,
 0x57182A, 0xD154D1, 0x26359F, 0xA07964, 0xACE092, 0x2AAC69,
 0xB5D37E, 0x339F85, 0x3F0673, 0xB94A88, 0x87B4A6, 0x01F85D,
 0x0D61AB, 0x8B2D50, 0x145247, 0x921EBC, 0x9E874A, 0x18CBB1,
 0xE37B16, 0x6537ED, 0x69AE1B, 0xEFE2E0, 0x709DF7, 0xF6D10C,
 0xFA48FA, 0x7C0401, 0x42FA2F, 0xC4B6D4, 0xC82F22, 0x4E63D9,
 0xD11CCE, 0x575035, 0x5BC9C3, 0xDD8538 );



# Since the packets are alway small, and we have ram we make an list that each item is a single bit. It is also a slow way to do it


def makeBitArray(buffer):
    current_index=0
    bitArray = (len(buffer)*8)*['0']
    for b in buffer:
        for i in range(0,8):
            if (b & 0x80) != 0:
                bitArray[current_index]='1'
            b<<=1
            current_index+=1
    return(bitArray)

def bitValue(bitArray,Start,Length):
#    print Start,Length
    s = ""
    for i in range (Start,Start+Length):
        s +=bitArray[i]
    return(int(s,2))

#(**********************************************************************
# * Compute the CRC24 checksum using a lookup table method.
# *
# *********************************************************************)
def crc_normal (Message_Buffer):
   crc = 0
#   print "CRC Length: " + str(len(Message_Buffer))
   for b in Message_Buffer:
       crc = crc24table[((crc >> 16) ^ b) & 0xFF] ^ (crc << 8);
   return(crc & 0xFFFFFF);


# ByteToHex From http://code.activestate.com/recipes/510399-byte-to-hex-and-hex-to-byte-string-conversion/

def ByteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    hex = []
    for aChar in byteStr:
        hex.append( "%02X " % aChar )

    return ''.join( hex ).strip()



class RTCM3:
    def __init__ (self,default_output_level):
        self.undecoded=bytearray("")
        self.buffer=bytearray("")
        self.default_output_level=default_output_level
        self.packet_ID=None
        self.packet_Length=None
        self.Dump_Levels=array("I")
        self.commands={}


        for i in range (RTCM3_Min_Message_ID,RTCM3_Max_Message_ID):
            self.Dump_Levels.append(default_output_level)

        files = glob.glob("DEFS/*.RTCM3")

        for file in files:
            sys.stderr.write("Loading File: " + file +"\n")
            rtcm3_Defs = RTCM3_Definition.rtcm3_Definition()
            rtcm3_Defs.read_from_file(file)
            sys.stderr.write ("Loaded Command: " + "{0}:{1}\n".format(rtcm3_Defs.Command_ID,rtcm3_Defs.Command_Name))
            self.commands[rtcm3_Defs.Command_ID]=rtcm3_Defs
#            self.commands.append(rtcm3_Defs)
#        pprint.pprint (self.commands[1033].fields)


    def add_data (self,data):
    # Add more received data into the system. Adding data does not mean that we will try and decode it.
        self.buffer+=data
#        print len(self.buffer)
#       print hexlify(self.buffer)

    def decode(self,packet_ID, packet_data):
        if packet_ID in self.commands:
            current_bit=0
            bitArray=makeBitArray(packet_data)
#            print "Bytes"
#            print ByteToHex(packet_data)
#            print packet_data
            for field in self.commands[packet_ID].fields:
#                print "Start Bit: " ,current_bit
#                print field["name"]
                if field["type"] == "UINT" :
                    field["value"]= bitValue(bitArray,current_bit,field["bitlength"])
                    current_bit+=field["bitlength"]
                elif field["type"] == "INT" :
                    field["value"]= bitValue(bitArray,current_bit,field["bitlength"])
                    current_bit+=field["bitlength"]
                elif field["type"] == "REPEAT" :
                    field["value"]= bitValue(bitArray,current_bit,field["bitlength"])
                    current_bit+=field["bitlength"]
                elif field["type"] == "PCHAR" :
                    length=bitValue(bitArray,current_bit,8)
#                    print "Length: {0} 0x{0:X}".format(length)
                    current_bit+=8
                    txt=""
                    for i in range(0,length):
                        txt+=chr(bitValue(bitArray,current_bit,8))
                        current_bit+=8
                    field["value"]=txt


        else:
            sys.stderr.write("No Decoder for {0}\n".format(packet_ID))


    def process_data (self, dump_decoded=False):

        if len (self.buffer) <  RTCM3_Min_Size :
#            print "To short"
            return Need_More

        if self.buffer[0] <> RTCM3_Preamble : # {It isn't a valid packet, skip to first start}
            for i  in range (0,len(self.buffer)):
    #                            print "in Did not get a STX: " + str(i)
                if (self.buffer[0] != RTCM3_Preamble) :
                    self.undecoded.append(self.buffer[0]);
                    del self.buffer[0];
                else:
                    break;
            return Got_Undecoded

        self.packet_Length = (self.buffer[RTCM3_Length_Location] & 0x03);
        self.packet_Length = self.packet_Length << 8;
        self.packet_Length = self.packet_Length | self.buffer[RTCM3_Length_Location+1];
#        print "Packet Length: {:X}".format(self.packet_Length)

        if (self.packet_Length+RTCM3_Min_Size) > len(self.buffer):
            return Need_More

        Computed_CRC = crc_normal(self.buffer[0:self.packet_Length+ RTCM3_First_Data_Location]);
#        print "Computed CRC {:X}".format(Computed_CRC)
        CRC = self.buffer[RTCM3_First_Data_Location + self.packet_Length];
        CRC = CRC << 8;
        CRC = CRC | self.buffer[RTCM3_First_Data_Location + self.packet_Length+1];
        CRC = CRC << 8;
        CRC = CRC | self.buffer[RTCM3_First_Data_Location + self.packet_Length+2];
#        print "CRC {:X}".format(CRC)


        if CRC == Computed_CRC:
            self.packet_ID = self.buffer[RTCM3_First_Data_Location];
            self.packet_ID = self.packet_ID << 4;
            self.packet_ID = self.packet_ID | ((self.buffer[RTCM3_First_Data_Location+1] >> 4) & 0x0F);
            self.packet=self.buffer[:self.packet_Length + RTCM3_Min_Size]
#            print "Packet"
#            print ByteToHex(self.packet)
            packet_data=self.packet[RTCM3_First_Data_Location:self.packet_Length+RTCM3_First_Data_Location] # The packet
            self.buffer=self.buffer[self.packet_Length + RTCM3_Min_Size:]
            self.undecoded=bytearray("")
            self.decode(self.packet_ID,packet_data)
            return Got_Packet
        else:
#            print "Invalid"
            del self.buffer[0] #Always delete the first byte since it failed the CRC
            if self.buffer[0] <> RTCM3_Preamble : # {It isn't a valid packet, skip to first start}
                for i  in range (0,len(self.buffer)):
                    if (self.buffer[0] != RTCM3_Preamble) :
                        self.undecoded.append(self.buffer[0]);
                        del self.buffer[0];
                    else:
                        break;
            return Got_Undecoded



    def dump (self,dump_undecoded=False,dump_status=False,dump_decoded=False,dump_timestamp=False):
        if self.Dump_Levels[self.packet_ID] :
            if dump_timestamp :
               print datetime.now()
            if dump_decoded :
                print "Packet Data: " + ByteToHex (self.packet)

            if self.packet_ID in self.commands:
                print ""
                print self.commands[self.packet_ID].Command_Name
                for field in self.commands[self.packet_ID].fields:
                    print "{0}: {1}".format(field["name"],field["value"])
                print ""




#        self.Handlers[self.packet_ID].dump(self.Dump_Levels[self.packet_ID]);


    def name (self):
        return str(self.packet_ID)

