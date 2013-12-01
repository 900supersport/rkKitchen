#!/usr/bin/python
############################################################################
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
from kitchen_utils import unpackboot_recovery, query_add, deployfiles, finalise_boot_recovery, custom_remove, custom_deploy
from utils import apply_sed, logerror

#    try:
#        
#    except Exception as e:
#        logerror('recovery::recoverymenu ',e,1 )


def recoverymenu():
    '''display recovery menu and process results'''
    try:
        my_menu = dict([
            ('a1', 'unpack recovery.img'), 
            ('b2', 'browse recovery'), 
            #('c3', 'init.d support'), 
            ('e5', 'finalise recovery'), 
            #('f6', 'Pack Kernel with fun_ CWM recovery'), 
            ('g=', '='), 
            ('h3', 'Custom remove'),
            ('j4', 'Custom deploy'),
            ('t=', '='), 
            ('vm', 'main menu'), 
            ('z=', '=')
            ])
        choice = mymenu(my_menu,'Enter selection :')

        if choice in ('1'):
            unpackrecovery()
        elif choice in ('2'):
            browse_recovery()
        elif choice in ('5'):
            finalise_recovery()
        #elif choice in ('6'):
        #    pack_CWM_recovery()
        else:
            pass
        
        if choice not in ('m','M'):
            recoverymenu()   
    except Exception as e:
        logerror('recovery::recoverymenu ',e,1)
        #raise


def browse_recovery():
    '''launch natilus and point at recovery'''  
    try:
        os.system('sudo ' + KitchenConfig.KitchenConfig.browser + ' working/recovery')
    except Exception as e:
        logerror('recovery::browse_recovery ',e,1)
        #raise 
 
 
def finalise_recovery():
    '''finalise the recovery image'''
    try:
        finalise_boot_recovery('recovery.img')
    except Exception as e:
        logerror('recovery::finalise_recovery ',e,1)
        #raise        

 
def unpackrecovery():
    '''unpack a recovery.img'''
    try:
        unpackboot_recovery('recovery.img')        
    except Exception as e:
        logerror('recovery::unpackrecovery ',e,1)
        #raise        
