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
############################################################################

#import os
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
        choice = mymenu(my_menu,'Enter selection :')

        if choice in ('1'):
            parse_parameter()
        elif choice in ('2'):
            display_params()
        elif choice in ('3'):
            editparameter_menu()
        else:
            pass
        
        if choice not in ('m','M'):
            parameter_menu()   

    except Exception as e:
        logerror('parameter::parameter_menu ',e,1)

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
    header()
    printparameter()       
    
    pprint('=') 
    pprint ('1 Resize system')
    pprint ('2 Apply change')
    pprint ('m parameter menu')
    pprint ('=')
    choice = raw_input('Enter selection :')    
    if choice in ('1'):
        ResizeSystem()
    elif choice in ('2'):
        applychanges()
        
    if choice not in ('m','M'): 
        editparameter_menu()

def applychanges():
    '''apply the current parameter changes to system and parameter files

'''
    rominfo.rominfo.applyparameterchanges()

def ResizeSystem():
    syssizeH, syssizeI, syssizeM, syssizeG = getsizes(rominfo.rominfo.system.size)
    sysosetH, sysosetI, sysosetM, sysosetG = getsizes( rominfo.rominfo.system.offset)
    
    size = long(raw_input('Enter new system size bytes ' + str(syssizeI) +  ' :'))

    if size != syssizeI:
        pprint('=')
        pprint( 'Resizing')

        size =long(math.ceil( float(size)/4096)) *4096
        newuseroffsethex = hex((size + sysosetI)/512)[:-1]
        parth , partl = newuseroffsethex[:-3] ,newuseroffsethex[-3:]
        if partl != '000':
            parth = hex(long(parth,16)+1)[:-1]
            offsetupdate = 1  
            pprint('Recalculating User offset')
            newuseroffsethex = parth + '000' 
            pprint('User offset required ' + newuseroffsethex)
            pprint('Recalculating size of system to fill space')
            size = (long(newuseroffsethex,16) - long(sysosetH,16))*512
            pprint('New system size = ' + str(size) + ' ' + hex(size/512)[:-1])
            pprint('=')

        pprint('Applying these changes will adjust the parameters and system.img files.')
        apply = raw_input('Apply these changes Y/N:')
        if apply in ('y','Y'):
            rominfo.rominfo.system.size = hex(size/512)[:-1]
            rominfo.rominfo.user.offset = newuseroffsethex
            rominfo.rominfo.applyparameterchanges()
            pprint('Please select shrink system from the system menu to resize system.img')
            #shrinksystem()
    else:
        print 'No Change'              

    dummy = raw_input('press enter to continue')


        
def getsizes(hexsize):
    bsize = int(hexsize,16) * 512
    Msize = bsize / 1024 / 1024
    Gsize = Msize / 1024
    return hexsize, bsize, Msize, Gsize

def getcurrentparameterdatalines():
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
        
        
