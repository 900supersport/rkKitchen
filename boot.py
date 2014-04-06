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
import KitchenConfig

from kitchenUI import mymenu
from kitchen_utils import unpackboot_recovery, query_add, deployfiles, finalise_boot_recovery, custom_remove, custom_deploy, query_add_by_file
from utils import apply_sed, logerror

#    try:
#        
#    except Exception as e:
#        logerror('boot::parse_parameter ',e,1)


def bootmenu():
    '''display boot menu and process results'''
    try:
        my_menu = dict([
            ('a1', 'unpack boot.img'), 
            ('b2', 'build prop edits'), 
            ('c3', 'init.d support'), 
            ('d4', 'brand boot.img'), 
            ('e5', 'finalise boot'), 
            ('g=', '='), 
            ('h6', 'Custom remove'),
            ('j7', 'Custom deploy'),
            ('k8', 'Custom extend'),
            ('l9', 'Custom extend init.rk30board.rc'),
            ('p=', '='), 
            ('qw', 'broWse'),
            ('t=', '='), 
            ('vm', 'main menu'), 
            ('z=', '=')
            ])
        choice = mymenu(my_menu,'Enter selection :')

        if choice in ('1'):
            unpackboot()
        elif choice in ('2'):
            initrc_mount_system_rw(1)
        elif choice in ('3'):
            addinitd_support(1)
        elif choice in ('4'):
            brand_boot(1)
        elif choice in ('5'):
            finalise_boot()
        elif choice in ('6'):
            custom_remove('working/boot/')    
        elif choice in ('7'):
            custom_deploy('working/boot/')
        elif choice in ('8'):
            path = 'working/boot/init.rc'
            query_add_by_file(path,os.path.join(KitchenConfig.KitchenConfig.KitchenPath
                ,'processcontrol/queryaddinitrc'))     
            os.system('sudo ' + KitchenConfig.KitchenConfig.editor + ' ' + path)
        elif choice in ('9'):
            path = 'working/boot/init.rk30board.rc'
            query_add_by_file(path,os.path.join(KitchenConfig.KitchenConfig.KitchenPath
                ,'processcontrol/queryaddrk30board'))  
            logging.debug('boot::bootmenu sudo ' + KitchenConfig.KitchenConfig.editor + ' ' + path)
            os.system('sudo ' + KitchenConfig.KitchenConfig.editor + ' ' + path)
        elif choice in ('W','w'):
            browse_boot()
        else:
            pass
        
        if choice not in ('m','M'):
            bootmenu()  
              
    except Exception as e:
        logerror('boot::bootmenu ',e,1)


def addpreinstall(openforreview):
    '''query add preinstall support'''
    
    try:
        path = 'working/boot/init.rc'
        spath = os.path.join(KitchenConfig.KitchenConfig.KitchenPath, 'processcontrol/addpreinstall')
        with open(spath,'r') as sf:
            query_add(path, 'service preinstall', sf.read())
                   
        if openforreview ==1:            
            os.system('sudo ' + KitchenConfig.KitchenConfig.editor + ' ' + path)
    except Exception as e:
        logerror('boot::addinitd_support ',e,1)

        
def addinitd_support(openforreview):
    '''query add init.d support'''
    
    try:
        path = 'working/boot/init.rc'
        spath = os.path.join(KitchenConfig.KitchenConfig.KitchenPath, 'processcontrol/addinitdsupport')
        with open(spath,'r') as sf:
            query_add(path, 'service runparts', sf.read())
                    
        if openforreview ==1:            
            os.system('sudo ' + KitchenConfig.KitchenConfig.editor + ' ' + path)
    except Exception as e:
        logerror('boot::addinitd_support ',e,1)
       
        
def initrc_mount_system_rw(openforreview):    
    '''update init.rc to mount system rw'''
    
    try:
        sedpath = os.path.join(KitchenConfig.KitchenConfig.KitchenPath, 'processcontrol/init.rc_systemrw')
        apply_sed(sedpath
            ,'working/boot/init.rc'
            ,openforreview)
    except Exception as e:
        logerror('boot::initrc_mount_system_rw ' ,e,1)
            
 
def browse_boot():
    '''launch browser and point at working/boot'''  
    try:
        cmd = 'sudo ' + KitchenConfig.KitchenConfig.browser + ' working/boot'
        logging.debug('boot::browse_boot ' + cmd)
        os.system(cmd)   
    except Exception as e:
        logerror('boot::browse_boot ',e,1)

    
def unpackboot():
    '''unpack a simple boot.img'''
    try:
        unpackboot_recovery('boot.img') 
    except Exception as e:
        logerror('boot::unpackboot ' ,e,1)


def finalise_boot():
    '''pack up boot.img'''
    try:
        finalise_boot_recovery('boot.img')
    except Exception as e:
        logerror('boot::finalise_boot ' ,e,1)

        
def brand_boot(openforreview):
    '''brad boot.img'''
    try:
        spath = os.path.join(KitchenConfig.KitchenConfig.KitchenPath, 'processcontrol/bootdeploy')
        deployfiles(spath
            ,'working/boot/'
            ,openforreview)
    except Exception as e:
        logerror('boot::brand_boot ',e,1)



