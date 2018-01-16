#import os
import sys
import json
import csv
#import time
import re
#import string

#from csvchklib import *
#import cvschklib

# Written on Jan 12, 2018, coldest day in the office (8 Celcius)

# HISTORY
#
# OPEN
# Load files from sub-folder (parse filename)
# JSON definition, to allow multiple continuous int/float value ranges [array] of min/max values
# Verbose function to suppress all messages, warnings etc..
# check on field type
# Allow headers not be fixed to position in definition file.
# Allow header not to be required
# split up code in routines and move to csvchklib package
# regex check on header name in data-file (upper lower case etc..)
# continue after row error , set maximum number of errors

# 
# CLOSED
# 16/01/2018 Check header names
# 16/01/2018 Check row data columns equal to header
# 16/01/2018 Correct many bugs, excpetion handlers for file open and reads

error_data_max = 5
error_data_count = 0

print ("csvchk - CSV file validation tool - version 1.0")

if (len(sys.argv) < 3):
    sys.exit('Syntax: csvchk <data definition map file> <data definition file>')
   
DataDefinitionMapFileName = sys.argv[1]  
DataFileName = sys.argv[2]        
DataDefinitionFileName = ""

try:

    mapfile = open(DataDefinitionMapFileName, "r", encoding = "utf-8"); 

except Exception as exception:
    print ("Error: Could not open data definition map file %s" % DataDefinitionMapFileName)               
    sys.exit(1)
    
else:
    
    try:
        mapdata = json.load(mapfile)    
        mapfile.close() 
        maps  = mapdata['map']
        for mapping in maps:
            check = mapping['regex']   
            regexp = re.compile(check)
            match = regexp.match(DataFileName)
            if (match):
                #print(" match")   
                DataDefinitionFileName = mapping['file']
            #else:
                #print("No match %s" % check )     
    except Exception as exception:
        print ("Error: Possible invalid map data definition map file %s" % DataDefinitionMapFileName)               
        sys.exit(1) 
            
try:
    
    deffile = open(DataDefinitionFileName, "r", encoding = "utf-8");
 
except Exception as exception:
    #Old stuff from fooling around with Exceptions
    #type, value, traceback = sys.exc_info()
    #print('Error opening %s: %s %s' % (value.filename, value.strerror, type))       
    #sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
    #print('Error opening %s: %s %s' % (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
    print ("Error: Could not open Data Definition file %s" % DataDefinitionFileName)               
    sys.exit(1)

else:
    #Load CSV definition
    
    try:  
        data = json.load(deffile)
    except Exception as exception:
        print ("Error: Could not load Data Definition file %s" % DataDefinitionFileName)               
        sys.exit(1) 
    else:
        deffile.close()
     
    print ("CSV data file: %s" % DataFileName, flush=True)
    print ("CSV data definition file: %s" % DataDefinitionFileName, flush=True)
    print ("CSV data definition file uses schema file: %s" % data['meta']['schema'], flush=True)   
        
    defcols = 0
        
    try:                             
        with open(DataFileName, 'r') as csvfile:
            #dialect = csv.Sniffer().sniff(csvfile.read(1024))
            reader = csv.reader(csvfile, delimiter=',')
            stop = False
    
            # Validate the header 
            
            if (data['header']['required'] =="true"):
                #print("Header check ", end="", flush=True),
                try: 
                    row = next(reader)  
                    colnr  = 0                   
                    defcols = len(data['fields'])
                    #print ("cols = %d" % defcols)                   
                    while (colnr < defcols):
                        name  = data['fields'][colnr]['name']  
                        if (name != row[colnr]):
                            print ("Error: Column names mismatch expected %s got %s" % (name, row[colnr]), flush=True)
                            stop = True
                        colnr = colnr +1
                except Exception as exception:
                    print ("Error: Failed to read data file header %s" % DataFileName)               
                    stop = True 
                                        
            if (stop ==True):
                print("Error: Headers check Failed", end="", flush=True) 
                sys.exit(1) 
            else:
                print("Header check PASS", end="", flush=True)
                
            # Validate data records
             
            print("\n")       
            
            try:
                 
                rownr = 0
                result= ""
                #print ("result: %d" % result, flush=True)   
                
                for row in reader:

                    print("row:", rownr + 1, end='\n', flush=True)
                                     
                    cols  = len(row)
                              
                    # Check if number of columns in file are more  than in definition file.
                                            
                    if (cols != defcols):
                        result = "fault"
                        print('Error - Columns in row not equal to definition !', flush=True)     
                                               
                    if (result != "fault"):
                               
                        colnr  = 0
                        result = "" 
                        while (colnr < cols):                     
                            print("col:", colnr, end="", flush=True)
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
                            #print("", end="", flush=True)
                    rownr = rownr + 1
                    
                    if (result == "fault"):
                        error_data_count = error_data_count + 1
                        if (error_data_count > error_data_max):
                            sys.exit('Error: Data fault condition encountered and maximum number of allowed errors exceeded')
                        else:
                            result = ""                                                                
                    #if (rownr > 1000): break;     
                         
            except csv.Error as e:
                sys.exit('Error: file %s, line %d: %s' % (DataFileName, reader.line_num, e))
    
    except Exception as exception:    
        print ("Error: Problem opening or reading data file %s" % DataFileName)               
        sys.exit(1)     
      
   
# 

    
    