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

import rominfo
from kitchenUI import mymenu
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
            #('c3', 'init.d support'), 
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
        else:
            pass
        
        if choice not in ('m','M'):
            parameter_menu()   

    except Exception as e:
        logerror('parameter::parameter_menu ' )
        logerror(e)
        raise        
        

def display_params(): 
    '''diplay the current parameter data''' 
    try:
        print
        print rominfo.rominfo.tostring()   
        dummy = raw_input('press enter to continue')
    except Exception as e:
        logerror('parameter::display_params ' )
        logerror(e)
        raise 
        

def parse_parameter():
    '''parse parameter file and persist''' 
    
    parse_parameter_by_file('working/parameter')
    

def parse_parameter_by_file(pfile):
    '''parse the supplied parameter file saving the data to rominfo
    '''
        
    try:
        #read file
        with open(pfile) as f:
            myfile = f.readlines()
        
        #parse each line into 
        for line in myfile:
            cpos = line.find(':')
            key = line[:cpos].strip()
            value = line[cpos+1:].strip()
            rominfo.rominfo.setparm(key, value)
            if key == 'CMDLINE':
                cmdlinedata = value.split(':')

        #identify image date
        for i,v in enumerate(cmdlinedata):
            if v.find('(cache)') > 0 :
                idat = v 
                break

        #parse image data
        for i,v in enumerate(idat.split(',')):
            tpos = v.find('@')
            bpos = v.find('(')
            size = v[:tpos]
            offset = v[tpos+1:bpos]
            image = v[bpos+1:].strip(')')
            rominfo.rominfo.setimage(image,offset,size)
    
        rominfo.rominfo.Pickle()    
    except Exception as e:
        logerror('parameter::parse_parameter_by_File ' )
        logerror(e)
        raise
        
        
