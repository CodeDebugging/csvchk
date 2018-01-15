import os
import sys
import json
import csv
import time
import re
import string

# Written on Jan 12, 2018, coldest day in the office (8 Celcius)

# TODO
#
# This program is a work in progress.
#
# 1. Load file from subfolder
# 2. Check header names
# 3. JSON multiple continious int/float value ranges [][][]]
# 4. Verbose function to surporess warnings and matches


FlagHeader = True  # file has a header

print ("csvchk - CSV file validation tool - version 1.0")

if (len(sys.argv) < 3):
    sys.exit('Syntax: csvchk <data definition map file> <data definition file>')
   
DataDefinitionMapFileName = sys.argv[1]  
DataFileName = sys.argv[2]        
DataDefinitionFileName = ""

try:

    mapfile = open(DataDefinitionMapFileName, "r", encoding = "utf-8"); 

except Exception as exception:
    print ("Could not open data definition map file %s" % DataDefinitionMapFileName)               
    sys.exit(1)
    
else:
    mapdata = json.load(mapfile)    
    mapfile.close() 
    maps  = mapdata['map']
    for mapping in maps:
        check = mapping['regex']   
        regexp = re.compile(check)
        match = regexp.match(DataFileName)
        if (match):
            print(" match")   
            DataDefinitionFileName = mapping['file']
        else:
            print("No match %s" % check )     
            
try:
    
    file = open(DataDefinitionFileName, "r", encoding = "utf-8"); 

except Exception as exception:
    #Old stuff from fooling around with Exceptions
    #type, value, traceback = sys.exc_info()
    #print('Error opening %s: %s %s' % (value.filename, value.strerror, type))       
    #sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
    #print('Error opening %s: %s %s' % (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
    print ("[ERROR] Could not open Data Definition file %s" % DataDefinitionFileName)               
    sys.exit(1)

else:

    #Load CSV definition  
    data = json.load(file)
    file.close()
     
    print ("CSV data file: %s" % DataFileName, flush=True)
    print ("CSV data definition file: %s" % DataDefinitionFileName, flush=True)
    print ("CSV data definition file uses schema file: %s" % data['meta']['schema'], flush=True)   
                                            
    with open(DataFileName, 'r') as csvfile:
        #dialect = csv.Sniffer().sniff(csvfile.read(1024))
        reader = csv.reader(csvfile, delimiter=',')
        
        #validate the header 
        if (data['header']['required'] =="true"):
            print("Header check: ", end="", flush=True),
            header = next(reader),   
            cols   = 4
            colnr  = 0
            while (colnr < cols):
                #print(header[colnr])
                colnr = colnr +1         
            print("OK", end= "\r", flush=True)
          
        try:
            
            rownr = 0
            for row in reader:
  
                cols   = len(row)
                cols   = 28
                colnr  = 0
                result = "" 
                while (colnr < cols):
                    
                    print("row:", rownr + 1, end='', flush=True),
                    print(", col:", colnr, end="", flush=True)
                    print(", title:", data['fields'][colnr]['name'] + "", end="", flush=True)
                    print(", data:", row[colnr], end="\n", flush=True)
                                                                   
                    #if ((data['fields'][colnr]['constraints']['required'] == "true") and (row[colnr] == "")):                            
                    #    result = data['fields'][colnr]['enforce']['required']
                    #    print ( result, "- Required check", end="\r", flush=True)
                    #    if (result == "fault"): break  

                    if ((data['fields'][colnr]['constraints']['blank'] == "false") and (row[colnr] == "")):
                        result = data['fields'][colnr]['enforce']['blank']
                        if (result != ""): print ( result, "- Blank check",end="\r", flush=True)
                        if (result == "fault"): break
                        
                    if ((data['fields'][colnr]['constraints']['blank'] == "true") and (row[colnr] != "")):
                        result = data['fields'][colnr]['enforce']['blank']
                        if (result != ""): print ( result, "- Blank check",end="\r", flush=True)
                        if (result == "fault"): break 
                       
                    if (data['fields'][colnr]['constraints']['blank'] == "false"):               
                        values = data['fields'][colnr]['constraints']['values']
                        count = 0
                        if (values != ""):
                            Found = False
                            values = data['fields'][colnr]['constraints']['values']                             
                            for value in values:
                                if (value == row[colnr]): Found = True;    
                            if (Found == False):
                                result = data['fields'][colnr]['enforce']['values']
                                if (result != ""): print ( result, "- Invalid value, expected %s" % values, end="\r", flush=True)
                                if (result == "fault"): break
                                                        
                                      
                        if ((data['fields'][colnr]['constraints']['regex'] != "")):
                            check = data['fields'][colnr]['constraints']['regex']
                            regexp = re.compile(check)
                            match = regexp.match(row[colnr])
                            if (not match):
                                result = data['fields'][colnr]['enforce']['regex']
                                if (result != "" ): print ( result, "- RegEx check, expected %s" % check, end="\r", flush=True)
                                if (result == "fault"): break
                    
                            fieldtype = data['fields'][colnr]['constraints']['type']                                      
                            if (fieldtype == "int"):
                                minval = data['fields'][colnr]['constraints']['min']   
                                maxval = data['fields'][colnr]['constraints']['max']
                                value =  row[colnr]                  
                                if (value < minval ): 
                                    result = data['fields'][colnr]['enforce']['min']
                                    if (result != ""): print ( result, "- Number too low, expected < %s" % minval, end="\r", flush=True)
                                    if (result == "fault"): break
                                if (value > maxval ): 
                                    result = data['fields'][colnr]['enforce']['max']
                                    if (result != ""): print ( result, "- Number too high, expected > %s" % maxval,  end="\r", flush=True)
                                    if (result == "fault"): break 

                     
                    #time.sleep(.1)            
                    colnr = colnr + 1
                    print("", end="", flush=True)
                rownr = rownr + 1
                
                if (result == "fault"):  sys.exit('\nFault condition encountered - Program exit !\n')
                                
                #if (rownr > 1000): break;     
                     
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (DataFileName, reader.line_num, e))
            
      
   
# 

    
    