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
#
#   This module adds python methods that need to run as root
#
############################################################################
import sys
import logging
from utils import logerror

#    try:
#        
#    except exception as e:
#        logerror('KitchenRunasroot::mountsystem ',e,1)

def query_add(filepath, check, addition):
    '''check the file specified in filepath for the string 'check'
    and if not found add the text 'addition' to the end ofthe file
    '''
    
    try:
        #print 'query_add start'
        #print filepath
        #print check
        #print addition
        check = check.strip("'")
        check = check.strip('"')
        check = check.strip(' ')
        addition = addition.strip("'")
        addition = addition.strip('"')
        addition = addition.strip(' ')
        
        with open(filepath,'r+') as f:
            initrf = f.read()
            found = initrf.find(check)
            print('query_add::check: ' + check)
            #print('query_add::found: {}'.format(  found))
            print('query_add::addition: ' + addition)
            if found == -1:
                f.write('\n')
                f.write(addition.strip())
    except Exception as e:
        logerror('KitchenRunasroot::query_add ',e,1)


#Inspect the args and call methods as appropriate
if sys.argv[1] == 'query_add':
    i = 0
    print 'Execute query_add'
    
    query_add(sys.argv[2], sys.argv[3], sys.argv[4])
else:
    for arg in sys.argv: 
        print arg
        

