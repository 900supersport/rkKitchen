#!/usr/bin/python
#   
#   FreakTabKitchen www.freaktab.com
#
#   Copyright 2013 Brian Mahoney brian@mahoneybrian.wanadoo.co.uk
#
###########################################################################
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################   


#python imports
import sys
import logging

#900supersport imports
import KitchenConfig
import rominfo

from utils import CheckMakeFolders, GetCWD, logerror
from rkmainmenu import rkmainmenu

#    try:
#        
#    except Exception as e:
#        logerror('FreakTabKitchen::mountsystem ',e,1)


def StartKitchen():
    '''Set basic config and logging options, reads complete config and start the kitchen
    
    
The actual Kitchen Config and if present the rominfo in the current workspace will be read, required folders as per config will be created, and then the rkmainmenu will be displayed.
'''
    logmode = logging.INFO
    writemode = 'a'
    filename = 'kitchen.log'
    
    for arg in sys.argv: 
        if arg == 'debug':
            logmode = logging.DEBUG
        elif arg == 'overwrite':
            writemode = 'w'
        
        
    logging.basicConfig(filename= filename,
                            filemode=writemode,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logmode)
                      
    
    try:
        logging.info('====================================================================================')
        logging.info('Start FreakKitchen')
        logging.info(sys.version) 
        
        kc = KitchenConfig.KitchenConfig
        kc()
        kc.cwd = GetCWD()
        
        ri = rominfo.rominfo
        ri(KitchenConfig.KitchenConfig.ROMInfoLoc())

        CheckMakeFolders(kc.KitchenFolders())

        rkmainmenu()
        kc.Pickle()
        ri.Pickle()
    except Exception as e:
        logerror('FreakTabKitchen::StartKitchen ',e,1)
    finally:
        print 'Thankyou for using 900supersport''s FreakTab RK Kitchen'

StartKitchen()

