#!/usr/bin/python
#
#   
#   FreakTabKitchen www.freaktab.com
#
#   Copyright 2013 Brian Mahoney brian@mahoneybrian.wanadoo.co.uk
#
############################################################################
#
#   FreakTabKitchen is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   FreakTabKitchen is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with FreakTabKitchen.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
#   This module is a python reworking of FUKAUMI Naoki rkunpack
#############################################################################
# * Copyright (c) 2010, 2011 FUKAUMI Naoki.
# * All rights reserved.
# *
# * Redistribution and use in source and binary forms, with or without
# * modification, are permitted provided that the following conditions
# * are met:
# * 1. Redistributions of source code must retain the above copyright
# *    notice, this list of conditions and the following disclaimer.
# * 2. Redistributions in binary form must reproduce the above copyright
# *    notice, this list of conditions and the following disclaimer in the
# *    documentation and/or other materials provided with the distribution.
# *
# * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# */
#############################################################################

import argparse
import sys
import os

def getstring(buff):
    s=''
    i=1
    c=buff[i]
    while ord(c) != 0:
        i=i+1
        s=s + c
        c=buff[i]

    return s

def getint(buff):
    #print len(buff)
    a=ord(buff[0])
    b=ord(buff[1])
    c=ord(buff[2])
    d=ord(buff[3])
    
    return (a ^ b<<8 ^ c<<16 ^ d<<24) #^ 0xffffffff


def unpack_rkfw(image,buff):
    '''unpack rkww
    print 'rkfw'
'''
    print 'VERSION:{}.{}.{}\n'.format(ord(buff[8]),ord(buff[7]),ord(buff[6]))
    print 'unpacking'

    #get and write head of image
    isize = ord(buff[4])
    s= image + '-HEAD'
    with open(s,'w') as fw:
        fw.write(buff[:isize])

    #get and write Boot signatue
    ioff = getint(buff[0x19:0x19 + 0x4])
    isize = getint(buff[0x1d:0x1d + 0x4])
    
    if buff[ioff:ioff + 4] != 'BOOT':
        raise exception('rkunpack::unpack_rkfw no BOOT signature')

    s=image + '-BOOT'
    with open(s,'w') as fw:
        fw.write(buff[ioff:ioff + isize])

    #Check we now have an RKAF update.img and write it
    ioff = getint(buff[0x21:0x25])
    isize = getint(buff[0x25:0x29])        

    ioff = getint(buff[0x21:0x21 + 0x4])
    isize = getint(buff[0x25:0x25 + 0x4])

    
    if buff[ioff:ioff + 4] != 'RKAF':
        raise exception('rkunpack::unpack_rkfw no RKAF signature')

    print '{:08x}-{:08x} {} {} bytes'.format(ioff,ioff+isize-1,image,isize)
    
    with open('update.img','w') as fw:
        fw.write(buff[ioff:ioff + isize])

    print 'unpacking update.img'
    print '================================================================================'
    unpack_rkaf('update.img', buff[ioff:ioff + isize])
 
    #check and write the -MD5 image
    if (len(buff) - (ioff + isize) != 32):
        raise exception('rkunpack::unpack_rkfw invalid MD5 length')

    s=image + '-MD5'
    print "{:08x}-{:08x} {} 32 bytes\n".format(ioff, ioff + isize - 1, s)
    with open(s,'w') as fw:
        fw.write(buff[ioff + isize:ioff + isize + 32])

    

def unpack_rkaf(image,buff):
    '''unpack an rkaf image

'''
    fsize = getint(buff[0x4:0x4 + 0x4])

    if fsize != len(buff):
        print 'invalid file size (should be {} bytes) is {}'.format(fsize,len(buff))

    
    print 'FIRMWARE_VER:{}.{}.{}'.format( ord(buff[0x87]), ord(buff[0x86]), ord(buff[0x84]))
    print 'MACHINE_MODEL:{}'.format(getstring(buff[0x7:0x7 + 0xff]))
    print 'MACHINE_ID:{}'.format( getstring(buff[0x29:0x29 + 0xff]))
    print 'MANUFACTURER:{}'.format( getstring(buff[0x47:0x47 + 0xff]))

    count = getint(buff[0x88:0x88 + 4])

    print '\nunpacking {} files'.format(count)

    #put image table into p. I may have been over generous here
    p =buff[0x8b:0x8b + 0x70 * (count + 1)]
    while count > 0:
        name = getstring(p[0x0:0x0 + 0x70])
        fpath = getstring(p[0x20:0x20 + 0x70])
        
        nsize = getint(p[0x5d:0x5d + 0x4])
        ioff = getint(p[0x61:0x61 + 0x4])
        noff = getint(p[0x65:0x65 + 0x4])
        isize = getint(p[0x69:0x69 + 0x4])
        fsize = getint(p[0x6d:0x6d + 0x4])

        if fpath[:4] == 'SELF':
            print '----------------- {}:{}:0x{:x}@0x{:x} ({})'.format( name,fpath, nsize, noff, image)
        else:    
            print '{:08x}-{:08x} {}:{}'.format(ioff, ioff + isize - 1, name, fpath),

            if noff != 0xffffffff:
                print ':0x{:x}@0x{:x}'.format(nsize,noff),

            if fpath[:9] == 'parameter':#remove rkcrc signing
                ioff += 8
                fsize -= 10 #12

            #check for existance of required sub directories and make them
            a = os.path.dirname(fpath)
            if len(a) > 0:
                if os.path.exists(a):
                    pass
                else:
                    os.makedirs(a)

            #write the image
            with open(fpath,'w') as fw:
                fw.write(buff[ioff:ioff + fsize])

            #if it's signed then unpack 
            if buff[ioff:ioff + 4] in ('KRNL','PARM'):
                unpack_krnl(fpath,buff[ioff:ioff + fsize])

        #advance to next image in table    
        p = p[0x70:]
        count = count - 1

        print ' {} bytes'.format(fsize)
    print '================================================================================'


def unpack_krnl(image,buff):
    '''unpack a kernel image

-raw is simply an unsigned kernel
-symbol presumably a symbol table that is present in some kernels?
'''
    ksize = getint(buff[4:8])
    buff = buff[8:] #skip 4 char prefix and 32 bit size

    with open(image + '-raw','w') as fw:
        fw.write(buff[:ksize])

    buff = buff[ksize + 4 :] #this excludes the 32 bit crc of the signed kernel

    if len(buff) > 0: #if there is anything left write it to image-symbol
        with open(image + '-symbol','w') as fw:
            fw.write(buff)


def rkunpack(image):
    '''unpack the image file

The outputs of this should be congruent to FUN's rkunpack'''

    print 'Unpacking :' + image

    buff =''
    with open(image,'r') as f:
        buff = f.read()

    test = buff[:4]
    if test == 'RKFW':
        unpack_rkfw(image,buff)
    elif test == 'RKAF':
        unpack_rkaf(image,buff)
    elif test in ('KRNL','PARM'):
        unpack_krnl(image,buff)
    else:
        raise exception('rkunpack::rkunpack BAD IMAGE')
        

#__main__ for stand alone usage
if __name__ == "__main__":
    #parse the input. 1 mandatory input image 
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    args=parser.parse_args()

    rkunpack(args.image)
    



