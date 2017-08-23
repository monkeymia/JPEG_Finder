# JPEG_Finder
Read filesystem (FAT) raw and extract JPEG images. 

I have beend inspired by TestDisk and PhotoRec (http://www.cgsecurity.org/)
and wrote something myself in python. Unfortunately it does not recover more 
files (in my case) :-(.

This application reads raw data from a drive/partition (specified 
by argument --input_partition) and extracts JPEG files.
The extracted files are written into subfolder specified 
by argument --output_dir. 

The output_dir must have sufficent free memory and at another 
partition/drive than the input.

Usage:
python JPEG_Finder.py --output_dir=<path> --input_partition=<name>

Example (Windows):
python JPEG_Finder.py  --output_dir="C:/TEMPC/" --input_partition="E:"

Example (Linux):"
python JPEG_Finder.py --output_dir="/tmp/" --input_partition="sdb1"

Known Limitations:
* Requires Python 2.x (see https://www.python.org/)
* No speed optimization  - Runs 1 day for 32 GB SD-Card. 
  
  