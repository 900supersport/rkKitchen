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
import shutil
import logging

import rominfo

from kitchenUI import mymenu, pprint
from utils import logerror

#globals
cluto = 0   # clut offset
pl = 0      # palette length
datao = 0   # data offset
w = 0       # kernel data image width
h = 0       # kernel data image height
ds = 0      # kernel data image size

#    try:
#        
#    except Exception as e:
#        logerror('kernel::kernelmenu ',e,1)

def kernel_menu():
    ''' stand alone menu'''
    
    try:
        ri = rominfo.rominfo
        
        if ri.kernelImageSize <> '':
            getkerneldata()
            my_menu = dict([
                ('aa', 'Get Kernel image info'), 
                ('bb', 'Brand Kernel'), 
                ('t=', '='), 
                ('vm', 'main menu'), 
                ('z=', '=')
                ])
        else:
             my_menu = dict([
                ('aa', 'Get Kernel image info'), 
                ('t=', '='), 
                ('vm', 'main menu'), 
                ('z=', '=')
                ])   
                
        choice = mymenu(my_menu,'Enter selection :')
        
        if choice in ('a'):
            getkerneldata()
        elif choice in ('b'):
            if w > 0:
                brandkernel();
        elif choice in ('m','M'):
            
            print'============================================='
            print('Exiting')
            print'============================================='
            
        if choice not in ('m', 'M'):
            kernel_menu()         
            
    except Exception as e:
        logerror('kernel::kernelmenu ' ,e,1)        
        
        
def printkerneldata():  
    '''print kernel data
    '''
    try:     
        pprint( '=')
        pprint( 'ppllogo_RKlogo_clut offset:{0:x}'.format(cluto))
        pprint( 'Palette length: {0:d}'.format(pl))
        pprint( '=')
        pprint( 'logo_RKlogo_data offset: {0:x}'.format(datao))
        pprint( 'resolution: {0:d}'.format(w) +':{0:d}'.format(h)) 
        pprint( 'data size:{0:d}'.format(ds))
        
        pprint( '=')       
            
    except Exception as e:
        logerror('kernel::printkerneldata ',e,1)
 
            
def getkerneldata():
    '''get kernel data '''
    global cluto    # clut offset
    global pl       # palette length
    global datao    # data offset
    global w        # kernel data image width
    global h        # kernel data image height
    global ds       # kernel data image size

    
    try:
        fpath = 'working/kernel.img'
        s = os.stat(fpath).st_size
        logging.info('kernel size ')
        logging.info(s)
        
        with open(fpath, 'r') as fr:
            o = findstring(fr,'ppllogo_RKlogo_clut',s) 
            logging.info('kernel::getkerneldata o:' )
            logging.info(o)
            if o>= 0:
                fr.seek(o)
                
                cluto = o
                pl = int(fr.read(1).encode('hex'),16)
                
                
                o = findstring(fr,'logo_RKlogo_data',s) 
                logging.info('kernel::getkerneldata o:' )
                logging.info(o )
                if o>0:
                    fr.seek(o)
                    
                    datao = o
                    
                    w=int(fr.read(2).encode('hex'),16)
                    h=int( fr.read(2).encode('hex'),16)
                    ds = w * h + 4       
                    rominfo.rominfo.kernelImageSize = '{0:d}'.format(w) + ':' + '{0:d}'.format(h)      
        
    except Exception as e:
        logerror('kernel::getkerneldata ',e,1)


def findstring(f, target, size):
    '''find the first occurance of the string s in the file f

    '''
    l = len(target) 
    buff=f.read(l)
    while buff != target and f.tell() < size:
        buff=buff[1:] +f.read(1)
    if f.tell() != size:
        return  f.tell() 
    else:
        return -1
        

def brandkernel():   
    '''brand and sign kernel

    '''
    global cluto    # clut offset
    global pl       # palette length
    global datao    # data offset
    global w        # kernel data image width
    global h        # kernel data image height
    global ds       # kernel data image size
    
    try:
        print
        print
        pprint('=')
        pprint('... Branding Kernel ')
        pprint('... opening  working/kerneltmp.img for read')
        
        with open('working/kernel.img', 'r') as fr:
            skipbytes=0
            sig=fr.read(4)
            
            pprint('... Checking for signature')
            if sig == 'KRNL':
                skipbytes=8
                pprint('... signature found')
        
            fr.seek(skipbytes)  #skip first 8 bytes to remove signing
            
            pprint('... opening  working/kerneltmp.img for write')
            #open a file to build our branded kernel into
            with open('working/kerneltmp.img', 'w') as fw:
                
                pprint( '... read write the kernel up to clut ')
                pprint( '... adjust for the signature as required ')
                fw.write(fr.read(cluto-skipbytes))
                
                pprint( '... open the clut for read and write to kerneltmp ')
                with open('localdeploy/logo_clut') as ft:
                
                    #iterate the clut
                    for c in iter(lambda: ft.read(1),""):
                        #write into our output 
                        fw.write(c)
                        
                        #skip this byte from the source
                        fr.read(1)
                        
                pprint( '... read write through to the logo_data')
                fw.write(fr.read(datao-fr.tell()))
                
                pprint ('... open the image data for read and write to kerneltmp ')
                with open('localdeploy/logo_data') as ft:
                    #iterate the data
                    for c in iter(lambda: ft.read(1),""): 
                        #write it to our output
                        fw.write(c)
                        #skip corresponding byte from source
                        fr.read(1)
                
                pprint( '... Write remainder of kernel')
                #iterate and write the remainder ofthe source
                for c in iter(lambda: fr.read(1),""): 
                        fw.write(c)
        
        pprint( '... sign the kernel and move branded kernels to working/brand')
        os.system('rkcrc -k working/kerneltmp.img working/brand/kernel.img')
        
        #rename the temp file
        os.rename('working/kerneltmp.img','working/brand/uskernel.img')
    except Exception as e:
        logerror('kernel::brandkernel ',e,1)                      
