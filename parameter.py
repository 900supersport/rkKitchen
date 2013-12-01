#!/usr/bin/python
#
#   
#   FreakTabKitchen www.freaktab.com
#
#   Copyright 2013 Brian Mahoney brian@mahoneybrian.wanadoo.co.uk
#
#   <version>2.0.1</version>
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
############################################################################

import os
import logging
import math

import rominfo
from kitchenUI import mymenu, header, pprint
from utils import logerror

#    try:
#        
#    except Exception as e:
#        logerror('parameter::parse_parameter ',e,1)

def parameter_menu():
    '''display parameter menu and process results'''
    
    try:
        my_menu = dict([
            ('a1', 'read parameters'), 
            ('b2', 'display parameters'), 
            ('c3', 'Edit Parameters'), 
            #('e5', 'finalise recovery'), 
            #('g=', '='), 
            #('h3', 'Custom remove'),
            #('j4', 'Custom deploy'),
            ('t=', '='), 
            ('vm', 'main menu'), 
            ('z=', '=')
            ])
        choice = mymenu(my_menu,'Enter selection :',checkvalid = True)

        if choice in ('1'):
            parse_parameter()
        elif choice in ('2'):
            display_params()
        elif choice in ('3'):
            editparameter_menu()
        elif choice in ('rR'):
            repairparams()
        else:
            pass
        
        if choice not in ('m','M'):
            parameter_menu()   

    except Exception as e:
        logerror('parameter::parameter_menu ',e,1)


def repairparams():
    '''attempt to repair the parameters file
'''
    try:
        repaired = False
        ri = rominfo.rominfo
        for b,err in ri.errorblocks:
            if err == 'size':
                imgsize = os.stat(os.path.join('working', b + '.img')).st_size
                newpsize = sizeinparamhex(sizeinwholeblocks(imgsize,int('0x2000',16)*512))
                Resizemtdblock(newpsize, b)
                repaired = True

        if repaired == True:
           pprint( 'Repairs have been made')
    
    except Exception as e:
        logerror('parameter::repairparams ',e,1)
        

def printmtdparts(mtdparts,indent):
    pprint( indent + mtdparts[:20])
    indent = indent + '    '
    parts = mtdparts[20:].split(',')
    for p in parts:
        pprint( indent + p)


def printcmdline(cmdline):
    pprint( 'CMDLINE:')
    parts = cmdline[8:].split(' ')
    indent = '    '
    for p in parts:
        if p[:20] == 'mtdparts=rk29xxnand:':
            printmtdparts(p,indent)
        else:
            pprint( indent + p)


def printparameter():
    lines =  getcurrentparameterdatalines().split('\n')
    for l in lines:
        if l[:8] == 'CMDLINE:':
            printcmdline( l)
        else: 
            pprint( l )       

def editparameter_menu():
    header(checkvalid = True)
    printparameter()       
    
    pprint('=') 
    pprint ('1 Resize system')
    #pprint ('2 Apply change')
    pprint ('m parameter menu')
    pprint ('=')
    choice = raw_input('Enter selection :')    
    if choice in ('1'):
        ResizeSystem()
##    elif choice in ('2'):
##        applychanges()
        
    if choice not in ('m','M'): 
        editparameter_menu()

##def applychanges():
##    '''apply the current parameter changes to system and parameter files
##
##'''
##    rominfo.rominfo.applyparameterchanges()

def sizetoparamsize(sizebytes,verbose = 0):
    syssizeH, syssizeI, syssizeM, syssizeG = getsizes(rominfo.rominfo.system.size)
    sysosetH, sysosetI, sysosetM, sysosetG = getsizes(rominfo.rominfo.system.offset)

    if sizebytes != syssizeI:
        if verbose == 1:
            pprint('=')
            pprint('Resizing')

        sizebytes = sizeinwholeblocks(sizebytes,4096)

        newuseroffsethex = sizeinparamhex(sizebytes + sysosetI)

        parth, partl = newuseroffsethex[:-3], newuseroffsethex[-3:]
        if partl != '000':
            parth = hex(long(parth,16)+1)[:-1]              
            newuseroffsethex = parth + '000' 
            sizebytes = (long(newuseroffsethex,16) - long(sysosetH,16))*512
            if verbose == 1:
                pprint('Recalculating User offset')
                pprint('User offset required ' + newuseroffsethex)
                pprint('Recalculating size of system to fill space')
                pprint('New system size = ' + str(sizebytes) + ' ' + hex(sizebytes/512)[:-1])
                pprint('=') 

    return sizebytes, newuseroffsethex           

def sizeinparamhex(sizebytes):
    if type(sizebytes) != long:
        sizebytes = long(sizebytes)
    return hex((sizebytes)/512)[:-1]

def sizeinwholeblocks(sizebytes,blocksize):
    '''return a long that is the smallest size that will accomadate sizebytes in full blocks
'''
    return long(math.ceil( float(sizebytes)/blocksize)) * blocksize

def ResizeSystem():
    
    import system

    try:
        syssizeH, syssizeI, syssizeM, syssizeG = getsizes(rominfo.rominfo.system.size)
    ##    sysosetH, sysosetI, sysosetM, sysosetG = getsizes( rominfo.rominfo.system.offset)
        
        size = long(raw_input('Enter new system size bytes ' + str(syssizeI) +  ' :'))

        if size != syssizeI:
            size, newuseroffsethex = sizetoparamsize(size,verbose = 1)        

            pprint('Applying these changes will adjust the parameters and system.img files.')
            apply = raw_input('Apply these changes Y/N:')
            if apply in ('y','Y'):
                Resizemtdblock(hex(size/512)[:-1],'system')    
##                rominfo.rominfo.system.size = hex(size/512)[:-1]
##                rominfo.rominfo.user.offset = newuseroffsethex
##                rominfo.rominfo.applyparameterchanges()
                system.shrinksystem()
        else:
            print 'No Change'              
            dummy = raw_input('press enter to continue')

    except Exception as e:
        logerror('parameter::ResizeSystem ',e,1)

def Resizemtdblock(blocksize,tgtblock):
    '''resize tgtblock to blocksize and adjust all following offsets
'''
    try:
        ri = rominfo.rominfo
        mtdblocks = ri.mtdblocks
        found = False
        trailingblocks = []

        #populate trailingblocks with our mtdblocks from our target onwards
        for block in mtdblocks:
            if block == tgtblock:
                found = True
            if found:
                trailingblocks.append(block)

        for block in trailingblocks:
            #adjust the size of our target and the offsets of the following blocks
            if block == tgtblock:
                newoffset, pfile = subsize(ri.parameterfile,tgtblock,blocksize)
            else:
                newoffset, pfile = suboffset(pfile,block,newoffset)

        ri.writeparameter(pfile)
        
        
    except Exception as e:
        logerror('parameter::Resizemtdblock ',e,1)

        
def subsize(pfile,image,hsize):
    '''for the given parameter file pfile, adjust image size to be hsize.
Return the hex offset required for the next block
'''
    try:
        if hsize[:2] == '0x':
            hsize = hsize[2:]
            
        tgt ='(' + image + ')'
        pos = pfile.find(tgt)

        newsize = '0x00000000'[:-len(hsize)] + hsize
        mtdblock = newsize + pfile[pos - 21:pos + len(tgt)][len(newsize):]

        offset = mtdblock[11:21]

        nextoffset =hex(int(newsize,16) + int(offset,16))
        pfile = pfile[:pos-21] + mtdblock + pfile[pos + len(tgt):]

    except Exception as e:
        logerror('parameter::subsize ',e,1)

    return nextoffset, pfile


def suboffset(pfile,image,hoffset):
    '''for the given parameter file pfile, adjust image offset to be hoffset.
Return the hex offset required for the next block
'''
    try:
        if hoffset[:2] == '0x':
            hoffset = hoffset[2:]
            
        tgt ='(' + image + ')'
        pos = pfile.find(tgt)

        newhoffset = '0x00000000'[:-len(hoffset)] + hoffset
        pfile = pfile[:pos -10] + newhoffset + pfile[pos:]
        if pfile[pos-12] =='-':
            nextoffset ='-'
        else:
            size = pfile[pos-21:pos-11]
            newhoffset = hex(int(size,16) + int(newhoffset,16))
    except Exception as e:
        logerror('parameter::offset ',e,1)
        
    return newhoffset, pfile

        
def getsizes(hexsize):
    if hexsize == '-':
        bsize = -1
        Msize = -1
        Gsize = -1
    else:
        bsize = int(hexsize,16) * 512
        Msize = bsize / 1024 / 1024
        Gsize = Msize / 1024
    return hexsize, bsize, Msize, Gsize

def getcurrentparameterdatalines():
    try:
        sdata =  rominfo.rominfo.parameterfile
            
        syssizeH, syssizeI, syssizeM, syssizeG = getsizes(rominfo.rominfo.system.size)
        userdatasizeH, userdatasizeI, userdatasizeM, userdatasizeG = getsizes(rominfo.rominfo.userdata.size)
            
            
        sdata = sdata + ' \n' + 'Current system size:'
        sdata = sdata + '\n' + '    Hex as paramters :' + syssizeH
        sdata = sdata + '\n' + '    bytes            :' + str(syssizeI)
        sdata = sdata + '\n' + '    Mbytes           :' + str(syssizeM)
        sdata = sdata + '\n'   
        sdata = sdata + ' \n' + 'Current userdata (app space) size:'
        sdata = sdata + '\n' + '    Hex as paramters :' + userdatasizeH
        sdata = sdata + '\n' + '    bytes            :' + str(userdatasizeI)
        sdata = sdata + '\n' + '    Mbytes           :' + str(userdatasizeM)  
        sdata = sdata + '\n' + '    Gbytes           :' + str(userdatasizeG)
        
        rdata = sdata.replace('\n\n','\n')
        while rdata != sdata:
            sdata = rdata
            rdata = sdata.replace('\n\n','\n')
    except Exception as e:
        logerror('parameter::getcurrentparameterdatalines ',e,1)

    return rdata

def display_params(): 
    '''diplay the current parameter data''' 
    try:
        print
        printparameter()

        dummy = raw_input('press enter to continue')
    except Exception as e:
        logerror('parameter::display_params ',e,1)
        

def parse_parameter():
    '''parse parameter file and persist''' 
    
    parse_parameter_by_file('working/parameter')
    

def parse_parameter_by_file(pfile):
    '''parse the supplied parameter file saving the data to rominfo
    '''
        
    try:
        rominfo.rominfo.storeparameterfile(pfile)
  
    except Exception as e:
        logerror('parameter::parse_parameter_by_File ',e,1)
        
        
