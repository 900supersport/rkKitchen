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
import os
import logging
import time

import KitchenConfig
import rominfo

from kitchenUI import  mymenu, pprint
from utils import finalisefilesystemimage, mountfileasfilesystem, logerror
from kitchen_utils import customremove, custom_deploy, query_add_by_file


def systemmenu():
    '''display system menu and process results'''
    
    my_menu = dict([
        ('a1', 'mount system.img'), 
        ('b2', 'unmount system'), 
        ('c=', '='),
        ('d3', 'grow system'),
        ('e5', 'custom remove'),
        ('g6', 'custom deploy'), 
        ('h7', 'custom build prop change'), 
        ('p=', '='), 
        ('qw', 'broWse'),
        ('s=', '='),
        ('tm', 'main menu'), 
        ('z=', '=')
        ])
    choice = mymenu(my_menu,'Enter selection :')

    if choice in ('1'):
        mountsystem()
    elif choice in ('2'):
        finalisesystem()
    elif choice in ('3'):
        growsystem()
    elif choice in ('5'):
        customremove('working/mntsystem/')    
    elif choice in ('6'):
        custom_deploy('working/mntsystem/')
    elif choice in ('7'):
        extendBuildprop(1)
    elif choice in ('W','w'):
        browse_system()
    else:
        pass
    
    if choice not in ('m','M'):
        systemmenu()


def resizerequired():
    '''return an int comparing the current system.img filesize to the ROMs configured systemsizeShrink()
    
    '''
    
    rv = 1 
    try:
        ri = rominfo.rominfo
        ss = os.path.getsize('working/system.img')
        if ri.systemsizeShrink() == ss:
            rv = 0       
        elif ri.systemsizeShrink() > ss:
            rv = -1
        else:
            rv = 1
    except Exception as e:
        logerror('system::resizerequired ',e,1)
    finally:
        return rv


def makebusyboxlinks(linkfilename):
    '''create busy box links as specified in the file linkfliename 
    '''
    try:
        path = os.path.expanduser(linkfilename)
        with open(path,'r') as f:
            for line in f:
                cl = line.strip();
                if cl[:1] <> '#' and len(cl) > 0:
                    os.system('sudo ' + cl)
    except Exception as e:
        logerror('system::makebusyboxlinks ' , e, 1)


def extendBuildprop(edit):
    '''Extend build properties
    
    edit = 1 to open the file in the configured editor once the changes made
    '''
    
    try:    
        path = 'working/mntsystem/build.prop'
        query_add_by_file(path,os.path.expanduser('~/pykitchen/processcontrol/queryaddbuild.prop') )  
        if edit ==1:
            kc = KitchenConfig.KitchenConfig
            os.system('sudo ' + kc.editor + ' working/mntsystem/build.prop')
    except Exception as e:
        logerror('system::extendBuildprop ' , e, 1)
            

def shrinksystem():
    '''shrink system.img to the size configured through KitchenConfig and rominfo
    
    '''
    logging.debug('shrinksystem start')
    
    try:
        c=rominfo.rominfo.systemsizeShrink() / 4096
        logging.debug('New size ' + str(c))
        resizesystem(c)
        logging.debug('shrinksystem complete')
    except Exception as e:
        logerror('system::shrinksystem ' , e, 1)

    
def growsystem():
    '''grow system.img to the size configured through KitchenConfig and rominfo
    
    '''
    logging.debug('growsystem start')
    
    try:
        c=rominfo.rominfo.systemsizeGrow() / 4096
        logging.debug('New size ' + str(c))
        resizesystem(c)
        logging.debug('growsystem complete')
    except Exception as e:
        logerror('system::growsystem ' , e, 1)

    
def resizesystem(c):   
    logging.debug('resizesystem start')
    
    try:
        print('Resize System:- Creating new img')
        os.system('dd if=/dev/zero of=working/system_ext4.img bs=4096 count=' + str(c))
        print('Resize System:- Make it ext4')
        
        os.system("sudo mkfs.ext4 -q -F -b 4096 working/system_ext4.img" )
        os.system('sudo mount -t ext4 -o loop working/system_ext4.img working/mntsystem_ext4/')
        os.system('sudo mount -t ext4 -o loop working/system.img working/mntsystem/')
        print('Resize System:- copy files accross, this may take a while ')
        os.system('sudo cp -r -v --no-dereference --preserve=all working/mntsystem/* working/mntsystem_ext4')
        print('Resize System:- tidy up')
        time.sleep(2)
        os.system('sudo umount working/mntsystem')
        time.sleep(2)
        os.system('sudo umount working/mntsystem_ext4')
        os.system('mv working/system.img working/system.img.orig')
        os.system('mv working/system_ext4.img working/system.img')
    except Exception as e:
        logerror('system::resizesystem ' , e, 1)
        
    logging.debug('resizesystem end')
    
    
def browse_system():
    '''launch natilus and point at working'''
    try:  
        kc = KitchenConfig.KitchenConfig
        os.system('sudo ' + kc.browser + ' working/mntsystem')  
    except Exception as e:
        logerror('system::browse_system ' , e, 1)
        
                 
def mountsystem():
    '''mount system.img in working/mntsystem'''
    try:
        mountfileasfilesystem('working/system.img', 'ext4' , 'working/mntsystem')
    except Exception as e:
        logerror('system::mountsystem ' , e, 1)
        
        
def finalisesystem():
    '''finalise the system image'''
    try:
        finalisefilesystemimage('working/mntsystem', 'working/system.img')
    except Exception as e:
        logerror('system::finalisesystem ' , e, 1)
        
