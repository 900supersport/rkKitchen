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
import logging

import KitchenConfig
import rominfo

from utils import logerror

#    try: 
#        
#    except Exception as e:
#        logerror('KitchenUI::pprint ',e,1)

def pprint(pstring):
    '''Pretty print the string
    
    Basic pretty print, if pstring = then a line of =
    othewise if it fits prepend '| ' then pad end with space ' |' to width
    '''
    try:
        logging.debug('Start pprint: ' + pstring)
        width = KitchenConfig.KitchenConfig.pwidth
        logging.debug('KitchenUI::pprint width: ' + str(width))
        
        pstring=pstring.rstrip()    
        lpstring = len(pstring)
        pad = width - 4 - lpstring
        if pstring[:1] == '=' and lpstring == 1:
            pstring = '='*width
        elif pad > 0 :
            pstring = '| ' + pstring + ' '*pad + ' |'
        print pstring
    except Exception as e:
        logerror('KitchenUI::pprint ',e,1) 
    
    logging.debug('end pprint')
    
    
def header():
    '''Display a generic header'''
    
    try:
        logging.debug('Start header')
        kernelimage = rominfo.rominfo.kernelImageSize
        print
        print
        pprint( '=')
        pprint( 'FreakTab RK ROM Kitchen by 900supersport v2.0.0')
        pprint( 'Brian Mahoney')
        pprint( '19 Oct 2013')
        pprint( 'www.freaktab.com')
        pprint( '=')
        pprint( 'Current ROM ' + rominfo.rominfo.romname)
        pprint( 'CWD ' + KitchenConfig.KitchenConfig.cwd)
        if kernelimage <> '':
            pprint( 'Kernel image size:' + kernelimage)
        pprint( '=')
    except Exception as e:
        logerror('KitchenUI::header ',e,1)  
    
    logging.debug('End header')
    
    
def mymenu(menuitems, prompt):
    '''format and display the supplied menu, prompt and return choice'''
    logging.debug('Start mymenu')
    
    try:
        header()
        for k in sorted(menuitems.keys()):
            if k[1:] == '=':
                pprint('=')
            else:
                pprint( k[1:] + ' ' + menuitems[k])
        choice=raw_input(prompt)
        return choice
    except Exception as e:
        logerror('KitchenUI::mymenu ',e,1)
        
           
