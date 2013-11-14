# System for displaying UI for creating DCOL commands

import pprint
from struct import *
from binascii import hexlify
import sys


class rtcm3_Definition:
    def __init__ (self):
        self.Command_Name = ""
        self.Command_ID = 0
        self.fields = []


    def read_from_file (self,filename):
        file=open(filename,"r")
        lines=file.readlines()
        file.close()
        if not lines:
            raise EOFError ('No lines in file ' + filename)

        if not (lines[len(lines)-1].strip() == "END:") :
            raise SyntaxError ('Did not end with a END: ' + filename)

        if not (lines[0].startswith("NAME:")):
            raise SyntaxError ('Did not start with NAME: ' + filename)
        else :
            self.Command_Name = lines[0][5:].strip()

        if not (lines[1].startswith("ID:")):
            raise SyntaxError ('Did not start with ID: ' + filename)
        else :
            self.Command_ID = int(lines[1][3:].strip(),0)

        current_Line=2

        in_selection=False
        combo=[]
        while current_Line < (len(lines)-1) :
            lines[current_Line]=lines[current_Line].strip()
#            print lines[current_Line]
            if lines[current_Line].startswith("INT:"):
                line = lines[current_Line][4:].strip()
                (bitlength,sep,line)=line.partition(':')
                bitlength=int(bitlength)
                (df_number,sep,line)=line.partition(':')
                df_number=int(df_number)
                name=line.strip()
                self.fields.append({'type': "INT" , 'name' : name, 'df_number':df_number, 'bitlength': bitlength ,'value':None})

            elif lines[current_Line].startswith("UINT:"):
                line = lines[current_Line][5:].strip()
                (bitlength,sep,line)=line.partition(':')
                bitlength=int(bitlength)
                (df_number,sep,line)=line.partition(':')
                df_number=int(df_number)
                name=line.strip()
                self.fields.append({'type': "UINT" , 'name' : name, 'df_number':df_number, 'bitlength': bitlength ,'value':None})

            elif lines[current_Line].startswith("REPEAT:"):
                line = lines[current_Line][7:].strip()
                (bitlength,sep,line)=line.partition(':')
                bitlength=int(bitlength)
                (df_number,sep,line)=line.partition(':')
                df_number=int(df_number)
                name=line.strip()
                self.fields.append({'type': "REPEAT" , 'name' : name, 'df_number':df_number, 'bitlength': bitlength ,'value':None})

            elif lines[current_Line].startswith("PCHAR:"):
                line = lines[current_Line][6:].strip()
                (df_number,sep,line)=line.partition(':')
                df_number=int(df_number)
                name=line.strip()
                self.fields.append({'type': "PCHAR" , 'name' : name, 'df_number':df_number ,'value':None
                })

            else :
                print "Unknown Command: " + lines[current_Line]
                quit()

            current_Line +=1



