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
import KitchenConfig
import time

from utils import  QueryPickleLoad, PickleIt, logerror

#    try:
#        
#    except exception as e:
#        logerror('rominfo::mountsystem ' ,e ,1)
#        raise

class rominfo:
    '''encapsulate info re the ROM''' 
    initialised = 0
    rominfofilepath =''

    romname = 'un-initialised'
    romimgfilename = ''
    version = '1.1'
    MAGIC = 0
    CMDLINE = ''
    CHECK_MASK = 0
    ATAG = 0
    MACHINE = ''
    RECOVERY_KEY = ''
    COMBINATION_KEY = ''
    MACHINE_MODEL = ''
    FIRMWARE_VER = ''
    KERNEL_IMG = 0
    MACHINE_ID = ''
    MANUFACTURER = ''
    kernelImageSize =''
    misc = 0
    kernel = ''
    boot = ''
    recovery = ''
    backup = ''
    cache = ''
    userdata = ''
    kpanic = ''
    system = ''
    user = ''
    
    parameterfile = ''
    
    def __init__(self, rominfopath):
        '''Rom info

        
        '''
 
        logging.debug('Initialising rominfo')
        try:
            rominfo.rominfofilepath = rominfopath
            
            #test here to prevent reentry 
            if rominfo.initialised == 0:
                #prevent re-entry
                rominfo.initialised = 1
                
                logging.debug('attempt to pickleload rominfo')
                
                #attempt to load a saved config
                reader = rominfo(rominfopath) 
                reader = QueryPickleLoad(reader, rominfopath)
                
                logging.debug('attempt to pickleload rominfo completed')

                #copy values back from the reader
                rominfo.romname = reader.romname
                rominfo.romimgfilename = reader.romimgfilename
                rominfo.version = reader.version
                rominfo.MAGIC = reader.MAGIC 
                rominfo.CMDLINE = reader.CMDLINE
                rominfo.CHECK_MASK = reader.CHECK_MASK
                rominfo.ATAG = reader.ATAG
                rominfo.MACHINE = reader.MACHINE
                rominfo.RECOVERY_KEY = reader.RECOVERY_KEY
                rominfo.COMBINATION_KEY = reader.COMBINATION_KEY
                rominfo.MACHINE_MODEL = reader.MACHINE_MODEL
                rominfo.FIRMWARE_VER = reader.FIRMWARE_VER
                rominfo.KERNEL_IMG = reader.KERNEL_IMG
                rominfo.MACHINE_ID = reader.MACHINE_ID
                rominfo.MANUFACTURER = reader.MANUFACTURER
                rominfo.kernelImageSize = reader.kernelImageSize
                
                rominfo.misc = reader.misc
                rominfo.kernel = reader.kernel
                rominfo.boot = reader.boot
                rominfo.recovery = reader.recovery
                rominfo.backup = reader.backup
                rominfo.cache = reader.cache
                rominfo.userdata = reader.userdata
                rominfo.kpanic = reader.kpanic
                rominfo.system = reader.system
                rominfo.user = reader.user
                rominfo.parameterfile = reader.parameterfile

            #copy values into self for pickle useage
            self.romname = rominfo.romname
            self.romimgfilename = rominfo.romimgfilename
            self.version = rominfo.version 
            self.MAGIC = rominfo.MAGIC 
            self.CMDLINE = rominfo.CMDLINE
            self.CHECK_MASK = rominfo.CHECK_MASK
            self.ATAG = rominfo.ATAG
            self.MACHINE = rominfo.MACHINE
            self.RECOVERY_KEY = rominfo.RECOVERY_KEY
            self.COMBINATION_KEY = rominfo.COMBINATION_KEY
            self.MACHINE_MODEL = rominfo.MACHINE_MODEL
            self.FIRMWARE_VER = rominfo.FIRMWARE_VER
            self.KERNEL_IMG = rominfo.KERNEL_IMG
            self.MACHINE_ID = rominfo.MACHINE_ID
            self.MANUFACTURER = rominfo.MANUFACTURER
            self.kernelImageSize = rominfo.kernelImageSize
            
            self.misc = rominfo.misc
            self.kernel = rominfo.kernel
            self.boot = rominfo.boot
            self.recovery = rominfo.recovery
            self.backup = rominfo.backup
            self.cache = rominfo.cache
            self.userdata = rominfo.userdata
            self.kpanic = rominfo.kpanic
            self.system = rominfo.system
            self.user = rominfo.user
            self.parameterfile = rominfo.parameterfile
        except Exception as e:
            logerror('rominfo::__init__ ' ,e ,1)

            
    @staticmethod    
    def storeparameterfile(filename,depth = 0):
    
        try:
            with open(filename) as f:
                rominfo.parameterfile = f.read()
                    #read file
            
            with open(filename) as f:
                myfile = f.readlines()
            
            #parse each line into 
            for line in myfile:
                cpos = line.find(':')
                key = line[:cpos].strip()
                value = line[cpos+1:].strip()
                rominfo.setparm(key, value)
                if key == 'CMDLINE':
                    cmdlinedata = value.split(':')

            #identify image data
            for i,v in enumerate(cmdlinedata):
                logging.info(i)
                logging.info(v)
                if v.find('(cache)') > 0 :
                    idat = v 
                    break

            #parse image data
            for i,v in enumerate(idat.split(',')):
                tpos = v.find('@')
                bpos = v.find('(')
                size = v[:tpos]
                offset = v[tpos+1:bpos]
                image = v[bpos+1:].strip(')')
                rominfo.setimage(image,offset,size)
        
            rominfo.Pickle()

            if depth==0:
                #write additional parameter files based on this one
                kc = KitchenConfig.KitchenConfig
                for s in kc.parametersizes():
                    rominfo.writeparameterfile(s)

                os.system('rm working/parameter')
                os.system('cp working/parameter' + str(kc.defaultuserdataG) + ' working/parameter')
                time.sleep(2)
                rominfo.storeparameterfile('working/parameter',1)

            #now update based on the p file
        except Exception as e:
            logerror('rominfo::storeparameterfile ' ,e ,1)

    @staticmethod
    def applyparameterchanges():
        '''Update the persisted parameter file with the current values and regenerate system.img and parameter files

    '''
        f = rominfo.parameterfile
        kpendloc = f.find(',', f.find('(kpanic)'))+1
        sysendloc = f.find(',', f.find('(system)'))+1
        userendloc =  f.find('(user)')+6

        npf = f[:kpendloc]
        npf = npf + rominfo.submtdsize(f[kpendloc:sysendloc],rominfo.system.size)
        npf = npf + rominfo.submtdoffset(f[sysendloc:userendloc],rominfo.user.offset)
        npf = npf + f[userendloc:]

        rominfo.parameterfile = npf

        with open('working/parameter','w') as mp:
            mp.write(npf)

        rominfo.storeparameterfile('working/parameter')

    @staticmethod
    def newoffset(offset,growth):
        '''calculate new offset based on offset and growth
'''
        return hex((long(offset,16) * 512 + growth) / 512)[:-1]

    @staticmethod
    def writeparameterfile(userdatasize):
        '''write a parameter file with the specified userdata size
'''
        try:
            csh = rominfo.userdata.size
            #print csh
            currentsize = long(csh,16)* 512 
            udsb = long(userdatasize) * 1024 * 1024 * 1024
            growth = udsb - currentsize
            #print growth
            f = rominfo.parameterfile
            if growth == 0:
                npf = f
            else:
                chendloc = f.find(',', f.find('(cache)'))+1
                udendloc = f.find(',', f.find('(userdata)'))+1
                kpendloc = f.find(',', f.find('(kpanic)'))+1
                sysendloc = f.find(',', f.find('(system)'))+1
                userendloc =  f.find('(user)')+6

                uds = f[chendloc:udendloc]
                kps = f[udendloc:kpendloc]
                syss = f[kpendloc:sysendloc]
                us = f[sysendloc:userendloc]
                rest = f[userendloc:]

                nudsh = hex(udsb/512)[:-1]
                uds = rominfo.submtdsize(uds,nudsh)

                nkpo = rominfo.newoffset(rominfo.kpanic.offset,growth) 
                nsyso = rominfo.newoffset(rominfo.system.offset,growth)
                nuo = rominfo.newoffset(rominfo.user.offset,growth)
                
                kps = rominfo.submtdoffset(kps,nkpo)
                syss = rominfo.submtdoffset(syss,nsyso)
                us = rominfo.submtdoffset(us,nuo)

                npf = f[:chendloc]
                npf = npf + uds
                npf = npf + kps
                npf = npf + syss
                npf = npf + us
                npf = npf + rest

                #0x00400000@0x00088000(userdata)
                #0x00002000@0x00488000(kpanic) 
                #0x00114000@0x0048A000(system) 
                #-@0x0059E000(user) 
                
            with open('working/parameter' + str(userdatasize),'w') as f:
                f.write(npf)
        except Exception as e:
            logerror('rominfo::writeparameterfile ' ,e ,1)
            

    @staticmethod
    def submtdsize(mtdstring,size):
        '''substitues size in the mtdstring supplied
    '''
        #strip 0x
        size = size[2:].upper()
        mtdsize,mtdoffset = mtdstring.split('@')
        return mtdsize[:-len(size)] + size + '@' + mtdoffset

    @staticmethod
    def submtdoffset(mtdstring,offset):
        '''substitues size in the mtdstring supplied
    '''
        #strip 0x
        offset = offset[2:].upper()
        #offset = offset.upper
        mtdsize,mtdoffset = mtdstring.split('@')
        loc = mtdoffset.find('(')
        newoffset = mtdoffset[:loc][:-len(offset)] + offset + mtdoffset[loc:]
        
        return mtdsize + '@'  + newoffset

                                
    @staticmethod
    def setROMimgFilename(ROMimgFilename):
        '''static set ROMimgFilename and romname
        '''
        rominfo.romimgfilename = ROMimgFilename
        rominfo.romname = ROMimgFilename[:ROMimgFilename.rfind('.')]
    
    @staticmethod    
    def Pickle():
        '''static pick this class
        '''
        reader = rominfo(rominfo.rominfofilepath) 
        logging.debug('reader.romname : ' + reader.romname)
        logging.debug('rominfo.romname :' + rominfo.romname)
        PickleIt(reader, rominfo.rominfofilepath)
        
    @staticmethod     
    def tostring():
        '''static to string
        '''
        logging.debug('rominfo.tostring started')
        '''string representation of class'''
        rval = 'romname = '  + rominfo.romname + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'version = ' + rominfo.version + '\n'
        logging.debug('rominfo.tostring ' + rval)
        
        rval += 'FIRMWARE_VER = ' + rominfo.FIRMWARE_VER + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'MACHINE_MODEL = ' + rominfo.MACHINE_MODEL + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'MACHINE_ID = ' + rominfo.MACHINE_ID + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'MAUFACTURER = ' + rominfo.MANUFACTURER + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'MAGIC = ' + str(rominfo.MAGIC) + '\n'
        rval += 'ATAG = ' + (rominfo.ATAG) + '\n'
        rval += 'MACHINE = ' + rominfo.MACHINE + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'CHECK_MASK = ' + (rominfo.CHECK_MASK) + '\n'
        rval += 'KERNEL_IMG = ' + (rominfo.KERNEL_IMG) + '\n'
        rval += 'RECOVERY_KEY = ' + rominfo.RECOVERY_KEY + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'COMBINATION_KEY = ' + rominfo.COMBINATION_KEY + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += 'CMDLINE = ' + rominfo.CMDLINE + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += '================================================\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.misc.tostring() + '\n'
        rval += rominfo.kernel.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.boot.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.recovery.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.backup.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.cache.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.userdata.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.kpanic.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.system.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        rval += rominfo.user.tostring() + '\n'
        logging.debug('rominfo.tostring ' + rval)
        return rval
    
    @staticmethod
    def setimage(image,offset,size):
        '''assign to correct property'''
        if image == 'misc':
            rominfo.misc = imageflashinfo(image,offset,size)
        elif image == 'kernel':
            rominfo.kernel = imageflashinfo(image,offset,size)
        elif image == 'boot':
            rominfo.boot = imageflashinfo(image,offset,size)
        elif image == 'recovery':
            rominfo.recovery = imageflashinfo(image,offset,size)
        elif image == 'backup':
            rominfo.backup = imageflashinfo(image,offset,size)
        elif image == 'cache':
            rominfo.cache = imageflashinfo(image,offset,size)
        elif image == 'userdata':
            rominfo.userdata = imageflashinfo(image,offset,size)
        elif image == 'kpanic':
            rominfo.kpanic = imageflashinfo(image,offset,size)
        elif image == 'system':
            logging.info('rominfo::setimage system image ' + image)
            logging.info('rominfo::setimage system offset ' + offset)
            logging.info('rominfo::setimage system size ' + size)
            rominfo.system = imageflashinfo(image,offset,size)
        elif image == 'user':
            rominfo.user = imageflashinfo(image,offset,size)
 
    @staticmethod
    def setparm(parm,val):
        '''assign to the correct property'''
        if parm == 'MAGIC':
            rominfo.MAGIC = val
        elif parm == 'CMDLINE':
            rominfo.CMDLINE = val
        elif parm == 'CHECK_MASK':
            rominfo.CHECK_MASK = val
        elif parm == 'ATAG':
            rominfo.ATAG = val
        elif parm == 'MACHINE':
            rominfo.MACHINE = val
        elif parm == 'RECOVERY_KEY':
            rominfo.RECOVERY_KEY = val
        elif parm == 'COMBINATION_KEY':
            rominfo.COMBINATION_KEY = val
        elif parm == 'MACHINE_MODEL':
            rominfo.MACHINE_MODEL = val
        elif parm == 'FIRMWARE_VER':
            rominfo.FIRMWARE_VER = val
        elif parm == 'KERNEL_IMG':
            rominfo.KERNEL_IMG = val
        elif parm == 'MACHINE_ID':
            rominfo.MACHINE_ID = val
        elif parm == 'MANUFACTURER':
            rominfo.MANUFACTURER = val
            
    @staticmethod
    def systemsizeGrow():
    
        kc = KitchenConfig.KitchenConfig
        rv = max(int(rominfo.system.size,16) * 512,kc.maxsystemsize)
        #11:51:52,624 root INFO rominfo::systemsizeGrow current systemsize 576716800
        #11:51:52,625 root INFO rominfo::systemsizeGrow current maxsystemsize 0
        #11:51:52,625 root INFO rominfo::systemsizeGrow current rv 576716800
        logging.info('rominfo::systemsizeGrow current systemsize ' +str(int(rominfo.system.size,16) * 512))
        logging.info('rominfo::systemsizeGrow current maxsystemsize ' +str(kc.maxsystemsize))
        logging.info('rominfo::systemsizeGrow current rv ' +str(rv))
        if rv ==0:
            rv = kc.defaultsystemsize
        return rv
                
    @staticmethod
    def systemsizeShrink():
    
        kc = KitchenConfig.KitchenConfig
        rv = max(int(rominfo.system.size,16) * 512,kc.minsystemsize)
        logging.info('rominfo::systemsizeShrink current systemsize ' +str(int(rominfo.system.size,16) * 512))
        logging.info('rominfo::systemsizeShrink current minsystemsize ' +str(kc.minsystemsize))
        logging.info('rominfo::systemsizeShrink current rv ' +str(rv))
        if rv ==0:
            rv = kc.defaultsystemsize
        return rv
    
class imageflashinfo:
    '''represent an rk mnt point 
    
    as specified in the parameter file and used by rkflashtool
    '''
    def __init__(self,image,offset,size):
        self.image = image
        self.offset = offset
        self.size = size
        
    def tostring(self):
        '''present class as a string'''
        return self.image + '\t' + str(self.offset) + '\t' + str(self.size)       
    
    def flashdata(self):
        '''return offset and size as a string for use by rkflashtool'''
        return str(self.offset) + ' ' + str(self.size)


