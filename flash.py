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


import rominfo
from kitchenUI import mymenu
from utils import logerror
from parameter import parse_parameter, parse_parameter_by_file, repairparams

#    try:
#        
#    except Exception as e:
#        logerror('flash::parse_parameter ',e,1)

def flash_menu():
    '''display flash menu and process results'''

    try:
    
        ri = rominfo.rominfo
        
        my_menu = dict([
            ('a1', 'flash misc'), 
            ('b2', 'flash kernel'), 
            ('c3', 'flash boot'), 
            ('e4', 'flash recovery'), 
            ('g5', 'flash system'), 
            ('h6', 'flash parameters'),
            
            ('i7', 'clear cache'),
            ('j8', 'clear userdata'),
            ('k9', 'reboot'),
            ('pp', 'Pull ROM'),
            ('t=', '='), 
            ('vm', 'main menu'), 
            ('z=', '=')
            ])
            
        choice = mymenu(my_menu,'Enter selection :',checkvalid = True)
        
        if choice in ('1'):
            flash_singleimage('working/misc.img',ri.misc.flashdata())
        elif choice in ('2'):
            flash_singleimage('working/kernel.img',ri.kernel.flashdata())
        elif choice in ('3'):
            flash_singleimage('working/boot.img',ri.boot.flashdata())    
        elif choice in ('4'):
            flash_singleimage('working/recovery.img',ri.recovery.flashdata())
        elif choice in ('5'):
            flash_singleimage('working/system.img',ri.system.flashdata())
        elif choice in ('6'):
            flash_parameters()
        elif choice in ('7'):
            flash_clear('cache')
        elif choice in ('8'):
            flash_clear('userdata')
        elif choice in ('9'):
            flash_reboot()
        elif choice in ('Pp'):
            pullROM()
        elif choice in('Rr'):
            repairparams()
        else:
            pass
        
        if choice not in ('m','M'):
            flash_menu()    
        
    except Exception as e:
        logerror('flash::flash_menu ',e,1)

 
def flash_parameters():
    '''flash parameters to tab
    
    create a signed version then flash as follows
        rkflashtool w 0x0 0x20 working/parameters_crc
        rkflashtool w 0x400 0x20 working/parameters_crc
        rkflashtool w 0x800 0x20 working/parameters_crc
        rkflashtool w 0xc00 0x20 working/parameters_crc
        rkflashtool w 0x1000 0x20 working/parameters_crc
        rkflashtool w 0x1400 0x20 working/parameters_crc
        rkflashtool w 0x1800 0x20 working/parameters_crc
        rkflashtool w 0x1c00 0x20 working/parameters_crc
    '''     
    try:
        os.remove('working/parameters_crc')
    except:
        pass
    
    try:
        path ='rkcrc'
        os.system(path + ' -p working/parameter working/parameters_crc')
        
        flash_singleimage('working/parameters_crc','0x0 0x20')
        flash_singleimage_noprompt('working/parameters_crc','0x400 0x20')
        flash_singleimage_noprompt('working/parameters_crc','0x800 0x20')
        flash_singleimage_noprompt('working/parameters_crc','0xc00 0x20')
        flash_singleimage_noprompt('working/parameters_crc','0x1000 0x20')
        flash_singleimage_noprompt('working/parameters_crc','0x1400 0x20')
        flash_singleimage_noprompt('working/parameters_crc','0x1800 0x20')
        flash_singleimage_noprompt('working/parameters_crc','0x1c00 0x20')
        os.remove('working/parameters_crc')
        
        raw_input('press enter to continue') 
    except Exception as e:
        logerror('flash::flash_parameters ',e,1)
       

def flash_clear(image):
    '''clear-format and image'''
    
    print 'to be implemented clear ' + image
    
    
def flash_reboot():
    '''reboot the device'''
    try:
        s = 'sudo rkflashtool b '
        print s
        
        os.system(s)
    except Exception as e:
        logerror('flash::flash_reboot ',e,1)
 
    
def flash_singleimage_worker(image,params,prompt):
    '''flash a single image'''  
    try:
        s = 'sudo rkflashtool w ' + params + ' <' + image

        if prompt == 1:
            print s
            r = raw_input('press f to flash ')
            if r == 'f':
                os.system(s)
                raw_input('press enter to continue')
        else:
            os.system(s)

    except Exception as e:
        logerror('flash::flash_singleimage_worker ',e,1)
      
    
def flash_singleimage_noprompt(image,params):
    '''flash an image without prompt'''
    flash_singleimage_worker(image,params,0)
    

def flash_singleimage(image,params):
    '''flash an image with prompt'''
    flash_singleimage_worker(image,params,1)
    
    
#read methods
 
def pullROM():
    '''read parameters from tab
    
    rkflashtool r 0x1c00 0x20 working/parameters_read
    ''' 
    try:    
        #check_make_folder('read')
        ri = rominfo.rominfo
        
        read_singleimage('read/parameter','0x0 0x20')
        parse_parameter_by_file('read/parameter')
        
        #read_singleimage('read/misc.img',ri.misc.flashdata())
        read_singleimage('read/kernel.img',ri.kernel.flashdata())
        read_singleimage('read/boot.img',ri.boot.flashdata())  
        read_singleimage('read/backup.img',ri.backup.flashdata())      
        read_singleimage('read/recovery.img',ri.recovery.flashdata())
        read_singleimage('read/system.img',ri.system.flashdata())

        raw_input('press enter to continue')    
    except Exception as e:
        logerror('flash::pullROM ',e,1)
 
    
def read_singleimage(image,params):
    read_singleimage_worker(image,params,1)

    
def read_singleimage_noprompt(image,params):
    read_singleimage_worker(image,params,0)
        
    
def read_singleimage_worker(image,params,prompt):
    '''read a single image'''  
    
    try:
        s = 'sudo rkflashtool r ' + params + ' >' + image

        if prompt == 1:
            print s
            r = raw_input('press r to read ')
            if r == 'r':
                os.system(s)
            #raw_input('press enter to continue')
        else:
            os.system(s)
    except Exception as e:
        logerror('flash::read_singleimage_worker ',e,1)

        
