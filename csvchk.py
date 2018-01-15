import os
import sys
import json
import csv
import time
import re
# from csvchklib import fib, fib2
#import csvchklib
import string

# Written on Jan 12, 2018, coldest day in the office (8c)

#Todo
# Check headers
# if blank allowed, ignore other checks


FlagHeader = True  # file has a header

sys.argv[1] = "big.csv"
sys.argv[0] = "map.json"

print ("CHKCSV - CSV file validation tool - version 1.0")

if (len(sys.argv) < 2):
    sys.exit('Syntax: CHKCSV <data defintion file> <data definition map file>')
   
DataDefinitionMapFileName = sys.argv[0]  
DataFilename = sys.argv[1]        
DataDefinitionFileName = ""

try:

    mapfile = open(DataDefinitionMapFileName, "r", encoding = "utf-8"); 
except Exception as exception:
    print ("Could not open data definition map file %s" %sys.argv[1])               
    sys.exit(1)
    
else:
    mapdata = json.load(mapfile)    
    mapfile.close() 
    maps  = mapdata['map']
    for mapping in maps:
        check = mapping['regex']  
        DataDefinitionFileName = mapping['file']      
        regexp = re.compile(check)
        match = regexp.match(mapping['file'])
        if (match):
            DataDefinitionFileName = mapping['file']     
            
    #print("Definition file name = %s" % DataDefinitionFileName)               

#sys.exit('ends')
       
try:

    #file = open(sys.argv[1], "r+", encoding = "utf-8");
    file = open(DataDefinitionFileName, "r", encoding = "utf-8"); 

except Exception as exception:
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
    
    
    print ("CSV data file: %s" % DataFilename, flush=True)
    print ("CSV data definition file: %s" % DataDefinitionFileName, flush=True)
    print ("CSV data definition file uses schema file: %s" % data['meta']['schema'], flush=True)   
                                         
    #print(data['fields'])
    #print(data['fields'][0]['name'])
    #print(data['fields'][0]['constraints']['required'])
    #print(data['fields'][0]['constraints']['regex'])
    
    #filename = "sample.csv"
    filename = "big.csv"
    
    with open(DataFilename, 'r') as csvfile:
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
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
            
      
   
# 

    
    