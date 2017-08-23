#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import array
import datetime
import getopt
import sys
import os

if sys.version_info.major != 2 : 
    raise NotImplementedError, "This script requires python 2.x ! "

class Memory_Stream (object) : 

    MIN_SECTOR_SIZE_BYTES = 512 # FAT32; 16..32 MByte

    def __call__ \
        ( self
        , input_filename  = ""
        , input_partition = ""
        ) : 
        if input_filename : 
            filename = input_filename
        elif input_partition : 
            filename = self.partition_name (input_partition)
        else : 
            raise ValueError, "Either input_filename or input_partition must be specified."
        self.file_read (filename, self.data_decode) 
    # end def    
    
    def data_decode (self, sector, data_lst) :
        pass
    # end def 
    
    def file_read (self, filename, callback) :
        sector = -1
        f = None
        try :
            print "Info:open file '%s';" % (filename, )
            f = file (filename, "rb")
        except Exception, e :
            print \
                ( "Error:Cannot open file '%s'; %s; %s;" 
                % (filename, e.__class__.__name__, e)
                )
            f = None
        if f : 
            try :
                try :
                    data_str = "test"
                    while data_str : 
                        sector += 1                
                        data_str = f.read (self.MIN_SECTOR_SIZE_BYTES) 
                        if data_str :
                            data_lst = list (ord (c) for c in data_str)
                            if callable (callback) : 
                                callback (sector, data_lst)
                            else : 
                                raise NotImplementedError, "callback is not callable"
                except Exception, e :
                    print \
                        ( "Error:Cannot read from file '%s'; %s; %s;" 
                        % (filename, e.__class__.__name__, e)
                        )
                    raise
            finally :
                if f : 
                    f.close ()
    # end def
    
    def file_write (self, filename, text, print_info = True) :
        f = None
        dirname = ""
        try :
            dirname = os.path.dirname (filename)
            if dirname and not os.path.exists (dirname) :
                os.makedirs (dirname)
        except Exception, e :
            print \
                ( "Error:Cannot mkdir '%s'; %s; %s;" 
                % (dirname, e.__class__.__name__, e)
                )
            return
        try :
            if print_info :
                print "Info:open file '%s';" % (filename, )
            f = file (filename, "wb")
        except Exception, e :
            print \
                ( "Error:Cannot open file '%s'; %s; %s;" 
                % (filename, e.__class__.__name__, e)
                )
            f = None
        if f : 
            try :
                try :
                    f.write (text)
                except Exception, e :
                    print \
                        ( "Error:Cannot write to file '%s'; %s; %s;" 
                        % (filename, e.__class__.__name__, e)
                        )
                    raise
            finally :
                if f : 
                    f.close ()
    # end def
    
    def is_windows (self) :
        platform = sys.platform
        if platform == "win32" : 
            return True
        elif platform == "linux2" :
            print "Warning:Linux should work, but never tested."
            return False
        elif platform == "darwin" :
            print "Warning:Mac should work, but never tested."
            return False
        elif platform in \
            ( "cygwin"
            , "os2"
            , "os2emx"
            , "riscos"
            , "atheos"
            ) :
            raise NotImplementedError, "Operating System is not supported. platform=%s;" % platform
        return None
    # end def
    
    def partition_name (self, partition) :
        if not partition : 
            raise ValueError, partition
        if self.is_windows () : 
            # INFO: Direct Drive Access Under Win32
            # https://support.microsoft.com/en-us/help/100027/info-direct-drive-access-under-win32
            # To open a physical hard drive for direct disk access (raw I/O) in a 
            # Win32-based application, use a device name of the form \\.\PhysicalDriveN
            # where N is 0, 1, 2, and so forth, representing each of the physical drives 
            # in the system.
            # To open a logical drive, direct access is of the form :
            # \\.\X:
            # where X: is a hard-drive partition letter, floppy disk drive, or CD-ROM drive
            partition_name =  "\\\\.\\" + partition
        else : 
            partition_name =  "/dev/" + partition
        return partition_name
    # end def 
    
# end class

class JPEG_Finder (Memory_Stream) : 

    COLLECT_MAX_EXIF_BYTES = 200
    fcount = 0
    PREFIX = "OUT"
    MARKER_DCT = \
        { 0xC0  : "SOF0"
        , 0xC1  : "SOF1"
        , 0xC2  : "SOF2"
        , 0xC3  : "SOF3"
        , 0xC4  : "DHT"
        , 0xC5  : "SOF5"
        , 0xC6  : "SOF6"
        , 0xC7  : "SOF7"
        , 0xC8  : "JPG"
        , 0xC9  : "SOF9"
        , 0xCA  : "SOFA"
        , 0xCB  : "SOFB"
        , 0xCC  : "DAC"
        , 0xCD  : "SOFC"
        , 0xCE  : "SOFE"
        , 0xCF  : "SOFF"
        , 0xD0  : "RST0"
        , 0xD1  : "RST1"
        , 0xD2  : "RST2"
        , 0xD3  : "RST3"
        , 0xD4  : "RST4"
        , 0xD5  : "RST5"
        , 0xD6  : "RST6"
        , 0xD7  : "RST7"
        , 0xD8  : "SOI"
        , 0xD9  : "EOI"
        , 0xDA  : "SOS"
        , 0xDB  : "DQT"
        , 0xDD  : "DRI"
        , 0xE0  : "APP0"
        , 0xE1  : "APP1"
        , 0xE2  : "APP2"
        , 0xE3  : "APP3"
        , 0xE4  : "APP4"
        , 0xE5  : "APP5"
        , 0xE6  : "APP6"
        , 0xE7  : "APP7"
        , 0xE8  : "APP8"
        , 0xE9  : "APP9"
        , 0xEA  : "APPA"
        , 0xEB  : "APPB"
        , 0xEC  : "APPC"
        , 0xED  : "APPD"
        , 0xEE  : "APPE"
        , 0xFE  : "COM"
        }
    def __call__ \
        ( self
        , output_dir
        , input_filename  = ""
        , input_partition = ""
        ) : 
        self._output_dir = output_dir
        self.init_decoder ()
        super (JPEG_Finder, self).__call__ \
            ( input_filename  = input_filename
            , input_partition = input_partition
            )
    # end def    
    
    def init_decoder (self) :
        self.fdata              = array.array ("B")
        self.length_hi          = -1
        self.length_low         = -1
        self.last_byte_is_ff    = False
        self.byte_in_section    = -1
        self.section_marker     = -1
        self.markers            = set ()
        self.exif_text          = ""
    # end def    

    def data_decode (self, sector, data_lst) :
        self.jpeg_sections (data_lst, sector = sector)
    # end def 

    def jpeg_sections (self, data_lst, sector = None) :
        # https://en.wikipedia.org/wiki/JPEG
        # The file format known as "JPEG Interchange Format" (JIF) is specified in 
        # Annex B of the standard.
        # ... additional standards have evolved to address these issues. The first of 
        # these, released in 1992, was JPEG File Interchange Format (or JFIF), followed 
        # in recent years by Exchangeable image file format (Exif)
        # Both of these formats use the actual JIF byte layout, consisting of different 
        # markers, but in addition employ one of the JIF standard's extension points, 
        # namely the application markers: JFIF uses APP0, while Exif uses APP1. 
        # 
        # Summarized: 
        # Read 0xFF.
        # Read marker. 
        # Read the length specifier L and skip forward by L - 2 bytes. 
        # After an SOS (0xFFDA) segment (followed by compressed data) skip forward to the 
        # first 0xFF not followed by 0x00 or 0xD0-0xD8. 
        # Repeat from start until you encounter 0xFFD9.
        len_data = len (data_lst) 
        if len_data < 1 : 
            raise RuntimeError, "no data within sector=%s" % sector
        for i, byte in enumerate (data_lst) : 
            if  (   (self.section_marker == 0xE1) 
                and (len (self.exif_text) < self.COLLECT_MAX_EXIF_BYTES)
                ):  # Exif should be in section "APP1"
                if (byte > 0) and (byte < 256) : 
                    c = chr (byte)
                    if  (  c.isalnum () 
                        or c in (":", " ")
                        ) :
                        self.exif_text += c
            if self.last_byte_is_ff :
                marker_text = self.MARKER_DCT.get (byte, "")
                self.markers.add (marker_text)
                if byte == 0xFF :
                    self.last_byte_is_ff = True
                    if len (self.fdata) > 0 : 
                        self.byte_in_section += 1
                        self.fdata.append (byte)
                elif byte in \
                    ( 0x00 # byte shuffling within SOS segment
                    , 0x01 # reserved
                    , 0xD0 # reset within SOS segment
                    , 0xD1 
                    , 0xD2
                    , 0xD3
                    , 0xD4
                    , 0xD5
                    , 0xD6
                    , 0xD7
                    ) :
                    self.last_byte_is_ff = False
                    if len (self.fdata) > 0 : 
                        self.byte_in_section += 1
                        self.fdata.append (byte)
                    else : 
                        pass
                elif byte == 0xDA : # SOS
                    if len (self.fdata) > 0 : 
                        self.fdata.append (byte)
                        self.section_marker = byte
                        self.last_byte_is_ff = False
                        self.length_hi       = 0
                        self.length_low      = 0
                elif byte == 0xD8 : # SOI
                    if len (self.fdata) > 0 : 
                        self.jpeg_write_sections ()
                    self.fdata.append (0xFF)
                    self.fdata.append (byte)
                    self.section_marker = -1
                    self.last_byte_is_ff = False
                elif byte ==  0xD9 : # EOI
                    if len (self.fdata) > 0 : 
                        self.fdata.append (byte)
                        self.jpeg_write_sections ()
                    self.last_byte_is_ff = False
                else : 
                    if len (self.fdata) > 0 : 
                        self.fdata.append (byte)
                        self.section_marker = byte
                        self.byte_in_section = 0
                        self.last_byte_is_ff = False
                        self.length_hi       = -1
                        self.length_low      = -1
            elif self.section_marker != -1 :
                if self.length_hi == -1 : 
                    if len (self.fdata) > 0 : 
                        self.length_hi       = byte
                        self.byte_in_section = 1
                        self.fdata.append (byte)
                        self.last_byte_is_ff = False
                elif self.length_low == -1 : 
                    if len (self.fdata) > 0 : 
                        self.length_low      = byte
                        self.byte_in_section = 2
                        self.fdata.append (byte)
                        self.last_byte_is_ff = False
                else : 
                    length = (self.length_hi << 8) + self.length_low 
                    if len (self.fdata) > 0 : 
                        self.byte_in_section += 1
                        self.fdata.append (byte)
                    if (self.byte_in_section < length) : 
                        self.last_byte_is_ff = False
                    else :
                        self.last_byte_is_ff = bool (byte == 0xFF)
            elif byte == 0xFF :
                self.last_byte_is_ff = True
                if len (self.fdata) > 0 : 
                    self.byte_in_section += 1
                    self.fdata.append (byte)
    # end def 
    
    def jpeg_write_sections (self) :
        self.fcount += 1
        if  (   ("SOI" in self.markers) 
            and ("APP0" in self.markers) 
            and ("SOS" in self.markers) 
            and ("EOI" in self.markers) 
            ) :
            ext = ".jpg"
        else :
            ext = ".bin"
        ext = ".jpg"
        d = None
        if "Exif" in self.exif_text : 
            for i, c in enumerate (str (self.exif_text)) : 
                if i > 3  and c == ":" : 
                    t = self.exif_text [(i - 4):(i - 4 + 19)] # find begin of potential 2017:08:02 12:31:56
                    try :
                        d = datetime.datetime.strptime(t, "%Y:%m:%d %H:%M:%S") 
                    except Exception, e : 
                        pass
                    if d is not None :
                        break
        if d is not None : 
            base_name = d.strftime("%Y_%m_%d_%H_%M_%S")
            sub_dir = d.strftime("%Y_%m")
        else :
            base_name = "%s_%04d" % (self.PREFIX, self.fcount, )
            sub_dir = "%04d" % (self.fcount // 1000, )
        fname = os.path.join \
            ( self._output_dir
            , sub_dir
            , "%s%s" % (base_name, ext)
            )
        text  = self.fdata.tostring ()
        self.file_write (fname, text, print_info = False)
        info = []
        for text in  [fname] + sorted (list (self.markers)) : 
            if text :
                info.append ('"%s"' % text)
        print ",".join (info)
        self.init_decoder ()
    # end def 
    
# end class

if __name__ == '__main__':
    def usage () : 
        print "Info: This application reads raw data from a drive/partition (specified "
        print "Info: by argument --input_partition) and extracts JPEG files."
        print "Info: The extracted files are written into subfolder specified "
        print "Info: by argument --output_dir. "
        print "Info:"
        print "Info: The output_dir must have sufficent free memory and at another "
        print "Info: partition/drive than the input."
        print "Info: If a file is obviouly corrupted/incomplete then the file extension is .bin"
        print "Info:"
        print "Info: Usage:"
        print "Info: %s --output_dir=<path> --input_partition=<name>" % sys.argv [0]
        print "Info:"
        print "Info: Example (Windows):"
        print 'Info: %s --output_dir="C:/TEMPC/" --input_partition="E:"' % sys.argv [0]
        print "Info: Example (Linux):"
        print 'Info: %s --output_dir="/tmp/" --input_partition="sdb1"' % sys.argv [0]
        sys.exit ()
    # end def 
    try:
        opts, args = getopt.getopt \
            ( sys.argv[1:]
            , "h"
            , ["help", "output_dir=", "input_partition=", "input_filename="]
            )
    except getopt.GetoptError as err:
        # print help information and exit:
        print "Error: Failed to parse command line; err=%s" % (str(err), )
        usage(my_args, my_options_dct)
        sys.exit(2)
    input_filename  = None
    input_partition = None
    output_dir      = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o == "--input_partition":
            input_partition = a
        elif o == "--input_filename":
            input_filename = a
        elif o == "--output_dir":
            output_dir = a
        else : 
            print "Error:Unknown option=%s" % o
            usage()
    print "Info:input_partition=%s" % input_partition
    print "Info:output_dir.....=%s" % output_dir
    if not output_dir : 
        print "Error:output_dir is not specified."
        usage()
    if not (input_filename or input_partition) : 
        print "Error:input_partition is not specified."
        usage()
    if input_filename and not os.path.exists (input_filename) : 
        print "Error:input_filename not found."
        usage()
    e = JPEG_Finder ()
    e (output_dir, input_partition = input_partition)
    # e ("c:/TEMPC/RAW_JPEG/", input_filename = "x.bin")    
    # e ("F:/TEMPC/", input_partition = "H:")
    print "Info:Finished"
# END