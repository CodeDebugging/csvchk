# CSVCHK 

## Background

This tool was written to be able to check very large CSV files for correct data and formatting

## How it works

A JSON based 'Data definition file'  is used to define the correct format for the header and row data.
A JSON based 'Data definition map' file is used as a mandatory argument for the script. 
With this JSON file the script will find the correct data definition file to use for the specific CSV data file.
   
## How to create definition files

Create a 'Data definition file'
Create a 'Data definition map' file to map  data definition files to the data filename

## How to run

Run the program csvchk <data definition map file> <CSV file>


## Known issues

1. All files need to be in the same folder. loading definition, map  and CSV files using a path prefix won't work.
2. No header check yet  
 

 