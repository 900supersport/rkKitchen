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
import logging

import KitchenConfig
import rominfo

from utils import logerror

#    try: 
#        
#    except Exception as e:
#        logerror('KitchenUI::pprint ',e,1)

def pprint(pstring,error = 0):
    '''Pretty print the string
    
    Basic pretty print, if pstring = then a line of =
    othewise if it fits prepend '| ' then pad end with space ' |' to width
    '''
    try:
        logging.debug('Start pprint: ' + pstring)
        width = KitchenConfig.KitchenConfig.pwidth
        logging.debug('KitchenUI::pprint width: ' + str(width))
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        COL = '\033[0;34;47m'
        
        pstring=pstring.rstrip()    
        lpstring = len(pstring)
        pad = width - 4 - lpstring
        if pstring[:1] == '=' and lpstring == 1:
            pstring = COL + '='*width  + ENDC
        elif pad > 0 :
            if error == 1:
                pstring = FAIL + pstring + COL
            pstring = COL + '| ' + pstring + ' '*pad + ' |' + ENDC
        print pstring
    except Exception as e:
        logerror('KitchenUI::pprint ',e,1) 
    
    logging.debug('end pprint')
    
    
def header(checkvalid = False):
    '''Display a generic header'''
    
    try:
        logging.debug('Start header')
        kernelimage = rominfo.rominfo.kernelImageSize
        print
        print
        pprint( '=')
        pprint( 'FreakTab RK ROM Kitchen by 900supersport v2.0.1')
        pprint( 'Brian Mahoney')
        pprint( '1 Dec 2013')
        pprint( 'www.freaktab.com')
        pprint( '=')
        romname = rominfo.rominfo.romname
        pprint( 'Current ROM ' + romname)
        pprint( 'CWD ' + KitchenConfig.KitchenConfig.cwd)
        if kernelimage <> '':
            pprint( 'Kernel image size:' + kernelimage)
        pprint( '=')
        if romname != 'un-initialised' and checkvalid:
            ri = rominfo.rominfo
            invalid, errors = ri.validatemtdblocks()
            if invalid != 0:
                pprint( 'Ivalid ROM',1)
                for l in errors.split('\n'):
                    pprint(l, 1)
                pprint(' ')
                pprint('Press R to attempt repair',1)
                pprint('=')
    except Exception as e:
        logerror('KitchenUI::header ',e,1)  
    
    logging.debug('End header')
    
    
def mymenu(menuitems, prompt, checkvalid = False):
    '''format and display the supplied menu, prompt and return choice'''
    logging.debug('Start mymenu')
    
    try:
        header(checkvalid)
        for k in sorted(menuitems.keys()):
            if k[1:] == '=':
                pprint('=')
            else:
                pprint( k[1:] + ' ' + menuitems[k])
        choice=raw_input(prompt)
        return choice
    except Exception as e:
        logerror('KitchenUI::mymenu ',e,1)
        
           
