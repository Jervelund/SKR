#!/usr/bin/env python

from binascii import crc32 # CRC32
import sys
from struct import *

if len(sys.argv) == 1:
  print 'Useage:',sys.argv[0],'<filename>'
  exit()

def bruteforceWidthAndHeight(): # NOT GENERAL YET
  target = unpack('>i','\x35\x46\x89\x13')[0] # Checksum from file
  pre = "\x49\x48\x44\x52" # Constant bytes before our guess
  post = "\x08\x06\x00\x00\x00" # Constant bytes after our guess
  for i in xrange(600,700): # We knew the width was 666 before
    w = pack(">i",i) # Guess width
    for j in xrange(500,600): # Height was
      h = pack(">i",j) # Guess height
      crc = crc32(pre+w+h+post) & 0xFFFFFFFF
      if crc == target:
        print (pre+w+h+post).encode('hex')
        return

unitNameDict = {0:'unknown',1:'meter'}
def parseField(f,header,length):
  if header == 'IHDR':
    data = f.read(length)
    crcCalc = crc32(header+data)
    w,h,bit_depth,color_type,compression,filter_method,interlace = unpack('>iiBBBBB', data)
    if w == 0:
      print 'WIDTH VALUE OF ZERO IS INVALID'
    if h == 0:
      print 'WIDTH VALUE OF ZERO IS INVALID'
    print '  Header: Width:%i Height:%i BitDepth:%i ColorType:%i Compression:%i FilterMethod:%i Interlace:%i'%(w,h,bit_depth,color_type,compression,filter_method,interlace)
  elif header == 'tEXt':
    data = f.read(length)
    crcCalc = crc32(header+data)
    data = data.split('\x00')
    print '  Text block contains: "%s" = "%s"'%(data[0],data[1])
  elif header == 'pHYs':
    data = f.read(length)
    crcCalc = crc32(header+data)
    x,y,unit = unpack('>IIB', data)
    print '  Pixels per unit: x: %i y: %i unit: %i (%s)'%(x,y,unit,unitNameDict[unit])
  else:
    f.seek(length+4,1)
    return
  crcFile = unpack('>i',f.read(4))[0]
  if crcCalc != crcFile:
    print "  !! CRC mismatch !! we got: %x file contained: %x"%(crcCalc,crcFile)
    print "Attempt to guess offset height and width"

f = open(sys.argv[1], "rb")
try:
  header = f.seek(8)
  more_data = True
  while more_data == True:
    l = f.read(8)
    length, header = unpack('>i4s', l)
    print "Length:",length,"Header:",header
    # Print additionals + move pointer
    parseField(f,header,length)
    if header == 'IEND':
      more_data = False
finally:
  f.close()
