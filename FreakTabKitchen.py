#!/usr/bin/python
#   
#   FreakTabKitchen www.freaktab.com
#
#   Copyright 2013 Brian Mahoney brian@mahoneybrian.wanadoo.co.uk
#
#   <version>2.0.1</version>
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
import os

#900supersport imports
import KitchenConfig
import rominfo

from kitchen_utils import pprint
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

    if GetCWD() =='/home/brian/rkKitchen':
        os.chdir('/home/brian/Desktop/ROMS/cube/u30gt2/2.06_official')
        print GetCWD
               
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
        print 'use py crc = {}'.format(kc.usepycrc)
        
        ri = rominfo.rominfo
        ri(KitchenConfig.KitchenConfig.ROMInfoLoc())

        CheckMakeFolders(kc.KitchenFolders())

        rkmainmenu()
        kc.Pickle()
        ri.Pickle()
    except Exception as e:
        logerror('FreakTabKitchen::StartKitchen ',e,1)
    finally:
        pprint ('=')
        pprint ('Thank you for using 900supersport''s FreakTab RK Kitchen')
        pprint ('')
        pprint ('For support or even just to say thanks see')
        pprint ('=')
        pprint ('http://www.freaktab.com/showthread.php?8042-FreakTab-RK-ROM-Kitchen-by-900supersport-v2')
        print 


StartKitchen()

