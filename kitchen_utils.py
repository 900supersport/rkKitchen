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
import shutil
import glob
import time
import struct
import zipfile
import zlib

#900supersport imports
import KitchenConfig
import rominfo
from rkcrc import rkcrc as crc
 
from kitchenUI import header, pprint
from utils import CheckMakeFolders, finalisefilesystemimage, mountfileasfilesystem, CheckMakeFoldersRoot, apply_sed, checkfsimage, logerror
from parameter import parse_parameter

#    try:
#        
#    except Exception as e:
#        logerror('kitchen_utils::mountsystem ',e,1)
#        raise

def rkcrc(flag, infile, outfile):
    try:
        kc = KitchenConfig.KitchenConfig
        if kc.usepycrc == 0:
            r = os.system('rkcrc ' + flag + ' ' + infile + ' ' + outfile)
            if r > 256:
                kc.usepycrc = 1
                crc(flag, infile, outfile)
        else:
           crc(flag, infile, outfile)
        
    except Exception as e:
        logerror('kitchen_utils::mountsystem ',e,1)
        raise

def query_add(path, check, addition):
    '''if check not found in path, append addition
    '''
    try:
        kRar=os.path.join(KitchenConfig.KitchenConfig.KitchenPath, 'kitchenRunasroot.py')
        addition ="'" + addition + "'"
        check = "'" + check + "'"
        
        #call out to some python as root :-)
        os.system('sudo python ' + kRar + ' query_add ' + path + ' ' + check + ' ' + addition)
    except Exception as e:
        logerror('kitchen_utils::query_add ',e,1)


def query_add_by_file(filepath,deployfilename):
    '''iterate through deployfile adding lines to filepath for any cases where the key is not present
    '''
    try:
        logging.info('kitchen_utils::query_add_by_File filepath ' + filepath)
        logging.info('kitchen_utils::query_add_by_File deployfilename ' + deployfilename)
        kRar=os.path.join(KitchenConfig.KitchenConfig.KitchenPath, 'kitchenRunasroot.py')
        path = os.path.expanduser(deployfilename)
        with open(path,'r') as f:
            for line in f:
                cl = line.strip();
                if cl[:1] <> '#' and len(cl) > 0:
                    args = cl.split(',')
                    p=cl.find(",")
                    check = cl[:p]
                    addition ="'" + cl[p+1:] + "'"
        
                    #call out to some python as root :-)
                    os.system('sudo python ' + kRar + ' query_add ' + filepath + ' "' + check + '" "' + addition + '"')
    except Exception as e:
        logerror('kitchen_utils::query_add_by_File ',e,1)


def custom_remove(targetpath):
    '''Custom remove (ROM specific)'''
    try:
        pprint('=')
        pprint('ROM specific file removal: ' + targetpath)
        pprint('=')
        
        rfile = raw_input('Enter the path of your ROM specific removal file').strip().strip("'").strip('"')
        removefiles(rfile,targetpath);
    except Exception as e:
        logerror('kitchen_utils::custom_remove ',e,1)
                                            

def custom_deploy(deploypath):
    '''Custom deploy (ROM specific)'''
    
    try:
        pprint('=')
        pprint('ROM specific file deploy: ' + deploypath)
        pprint('=')
        
        dfile = raw_input('Enter the path of your ROM specific deploy file: ').strip().strip("'").strip('"')
        deployfiles(dfile,deploypath,1)
    except Exception as e:
        logerror('kitchen_utils::custom_deploy ',e,1)

def copyfilesworker(movefilename,sourceroot,asroot,verbose=0):
    mvcpfilesworker(movefilename,sourceroot,'cp',asroot,verbose)


def movefilesworker(movefilename,sourceroot,asroot = 1,verbose=0 ):
    mvcpfilesworker(movefilename,sourceroot,'mv',asroot,verbose)


def mvcpfilesworker(movefilename,sourceroot,op,asroot,verbose=0):
    try:
        serr=''
        path = os.path.expanduser(movefilename)
        
        with open(path,'r') as f:
            for line in f:
                cl = line.strip();
                if cl[:1] <> '#' and len(cl) > 0:
                    args = cl.split(',')
                    source = os.path.join(sourceroot, args[0].strip())
                    dest = os.path.join(sourceroot, args[1].strip())
                    if len(args) > 2:
                        destpath = args[2].strip()
                    else:
                        destpath = ''
                    
                    pth,fn =os.path.split(source)
                    
                    fn= os.path.join(destpath,fn)
                    logging.debug('kitchen_utils::mvcpfilesworker source' + source)
                    logging.debug('kitchen_utils::mvcpfilesworker dest' +  dest)
                    iszip = 0
                    lendest = len(dest)
                    if lendest > 3:
                        if dest[lendest-3:] == 'zip':
                            iszip = 1
                    logging.debug('kitchen_utils::mvcpfilesworker iszip' + str(iszip))
                    try:
                        if os.path.exists(source):
                            
                            if iszip == 1:
                                if verbose ==1:
                                    pprint( 'Zipping {} size {:,} kb'.format(source,os.stat(source).st_size/1024))
                                logging.debug('kitchen_utils::mvcpfilesworker ' + dest)
                                zf = zipfile.ZipFile(file=dest,mode='a',compression=zipfile.ZIP_DEFLATED)
                                #zf.printdir()
                                zf.write(source,fn)
                                zf.close()
                            else:
                                if verbose ==1:
                                    pprint( 'Processing {} size {:,} kb'.format(source,os.stat(source).st_size/1024))
                                logging.info('kitchen_utils::mvcpfilesworker ')
                                logging.info([dest])
                                CheckMakeFoldersRoot([dest])
                                moves = op + ' ' + source + ' ' + dest
                                if asroot==1:
                                    moves = 'sudo ' + moves
                                logging.debug('kitchen_utils::mvcpfilesworker moves :' + moves)
                                os.system(moves)  
                        else:
                            logging.debug('kitchen_utils::mvcpfilesworker source does not exist Source= ' + source)
                    except IOError as e:
                        logerror('kitchen_utils::mvcpfilesworker inner ',e,1)
                        serr = serr + 'could not move ' + sourceroot.strip() + args[0].strip() + '\n'   
        
        if serr <> '':
            print serr
            choice=raw_input('Press enter to continue')  
    
    except Exception as e:
        logerror('kitchen_utils::mvcpfilesworker ',e,1)


    
def movefiles(movefilename):
    '''move files 
    
    sample
    G, Superuser.apk, app/, 644
    '''
    
    try:
        movefilesworker(movefilename, 'working/mntsystem/')
        path = os.path.expanduser(movefilename)
    
    except Exception as e:
        logerror('kitchen_utils::movefiles ',e,1)

    
def deployfiles(deployfilename,deploydest,openforreview):
    '''deploy files 
    
    sample
    G, Superuser.apk, app/, 644
    '''
    
    try:
        serr=''
        deploydest = deploydest.strip()
        path = os.path.expanduser(deployfilename)
        globalroot = os.path.join(KitchenConfig.KitchenConfig.KitchenPath,'deployfiles')
        localroot = 'localdeploy/'
        with open(path,'r') as f:
            for line in f:
                cl = line.strip();
                if cl[:1] <> '#' and len(cl) > 0:
                    args = cl.split(',')
                    sourceroot = ''
                    if args[0] == 'G':
                        sourceroot = globalroot
                    elif args[0] == 'L':
                        sourceroot = localroot
                    try:
                        tgt = os.path.join(sourceroot, args[1].strip())
                        logging.info('kitchen_utils::deployfiles attempt deploy ' + tgt)
                        #if os.path.exists(tgt):
                        if len(glob.glob(tgt)) > 0:
                            if tgt.find('*') > 0:
                                flags = '-r '
                            else:
                                flags = ''

                            dest = os.path.join(deploydest, args[2].strip())
                            CheckMakeFoldersRoot([dest])
                            copys = 'sudo cp ' + flags + tgt + ' ' + dest
                            chmods = 'sudo chmod '  + args[3][3:] + ' ' + os.path.join(deploydest, args[2].strip(), args[1].strip())
                            logging.debug('copy :' + copys)
                            logging.debug('chmod :' + chmods)   
                            os.system(copys)   
                            os.system(chmods)
                    except IOError as e:
                        logerror(e)
                        
                        serr = serr + 'could not deploy ' + sourceroot.strip() + args[1].strip() + '\n'   
        
        if serr <> '':
            print serr
            choice=raw_input('Press enter to continue')
        
        if openforreview ==1:            
            os.system('sudo nautilus ' + deploydest)    
    
    except Exception as e:
        logerror('kitchen_utils::deployfiles ',e,1)
        

def customremove(targetpath):
    '''Custom remove (ROM specific)'''
    
    try:
        pprint('=')
        pprint('ROM specific file removal: ' + targetpath)
        pprint('=')
        
        rfile = raw_input('Enter the path of your ROM specific removal file').strip().strip("'").strip('"')
        removefiles(rfile,targetpath)
    except Exception as e:
        logerror('kitchen_utils::customremove ',e,1)


def removefiles(removefile,root):
    '''remove files from the location
    
    iterate removefile removing files from root
    moving them to the location specified in the file
        app/cube.0.3.0_v2963.apk, removed/app
    '''
    logging.debug('remove files start (removefile:root)(' + removefile + ':' + root)
    
    path = os.path.expanduser(removefile)
    with open(path,'r') as f:
        for line in f:
            cl = line.strip();
            args = cl.split(',')
            if cl[:1] <> '#' and len(cl) > 0:
                try:
                    print 'Attempt Move ' + cl
                    source = os.path.join(root, args[0].strip())
                    dest = os.path.join('working/', args[1].strip())
                    #if os.path.exists(source):
                    if len(glob.glob(source)) > 0:
                        logging.debug('copy ' + source + ' ' + dest )
                        logging.debug('Remove ' + source)
                        CheckMakeFolders([dest])
                        os.system('sudo cp ' + source + ' ' + dest)
                        #shutil.copy(source, dest)
                        os.system('sudo rm ' + root + args[0].strip())
                    else:
                        logging.debug(source + ' does not exist')
                except IOError as e:
                    #print 'error ' + root + args[0].strip()
                    logerror('kitchen_utils::removefiles ' ,e,0)
                    
    logging.debug('remove files END')
    logging.debug('================')
    

def browse(path):
    '''launch natilus and point at working'''  
    
    try:
        kc = KitchenConfig.KitchenConfig
        os.system('sudo ' + kc.browser + ' ' + path) 
    except Exception as e:
        logerror('kitchen_utils::browse ',e,1)
        

def copyImages():
    '''copy the unpacked image files to the working folder
    '''
    try:  
        pprint('Copy image and parameter files')  
        #and copy to working, no wilcard support so use glob
        for file in glob.glob(os.path.join(KitchenConfig.KitchenConfig.SourceROMUnpackedLoc(),'Image/*.img')):
            print file
            shutil.copy(file,'working')            
            
        shutil.copy(
            os.path.join(KitchenConfig.KitchenConfig.SourceROMUnpackedLoc(),'parameter')
            ,'working')
    except Exception as e:
        logerror('kitchen_utils::copyImages ',e,1)


def saveromdata():
    '''save the rom data to the rominfo
    '''
    try: 
        parse_parameter()
    except Exception as e:
        logerror('kitchen_utils::saveromdata ',e,1)      


def finalise_boot_recovery(image):
    '''pack up boot.img or recovery'''
    
    try:
        loc = image.find('.')
        folder = image[:loc]

        pprint('=')
        pprint('Finalising ' + image)
        print 'folder= ' + folder
        pprint('=')
        
        #check_make_folder('working/' + folder) 
        touch_and_zip_boot_recovery(folder,image)
        
        print 'os.rename ' ,
        print os.path.join('working', image),os.path.join('working', image + '.old')
        os.rename(os.path.join('working', image),os.path.join('working', image + '.old'))
        print 'renamed'
        #logging.debug('rkcrc -k working/custom' + image + '.gz '  + image)
        #os.system('rkcrc -k working/custom' + image + '.gz working/'  + image)
        rkcrc('-k', 'working/custom' + image + '.gz', 'working/' + image)
        
        pprint('=')
        pprint(image + ' finalised')
        pprint('=')  
    except Exception as e:
        logerror('kitchen_utils::finalise_boot_recovery ',e,1)


def touch_and_zip_boot_recovery(folder,image): 
    '''touch all files in the image setting the data to 1-1-1970
    '''
    try:   
        os.chdir(os.path.join('working', folder))
        os.system('sudo find . -exec touch -d "1970-01-01 01:00" {} \;')
        os.system('sudo find . ! -name "." | sort | sudo cpio -oa -H newc | sudo gzip -n >../custom'  + image + '.gz')
        os.chdir('../..')    
    except Exception as e:
        logerror('kitchen_utils::touch_and_zip_boot_recovery ',e,1)
            

def unpackboot_recovery(image):
    '''unpack a boot.img or recovery.img'''
    
    try:
        loc = image.find('.')
        folder = image[:loc]
        filepath = os.path.join('working/', image)
        
        with open(filepath,'rb') as f:
            disc = f.read(4)
        
        if disc == 'KRNL':
            logging.info('kitchen_utils::unpack_recovery boot.img signed KRNL')
            os.system('dd if=working/' + image + ' of=working/' + image + '-ramdisk.gz'
                + ' skip=8 bs=1 count=20000000')
        else:
            
            unpackBootRecoveryfile(filepath)
            logging.debug('kitchen_utils::unpack_recovery :')
            
        imagefolder = os.path.join('working', folder)    
        CheckMakeFolders([imagefolder])       
        os.chdir(imagefolder)
        
        #protect against this being first sudo request
        os.system('sudo ls')
            
        os.system('sudo gunzip < ../' + image + '-ramdisk.gz '
            + '| sudo cpio -i --make-directories')
         
        os.chdir('../..')
    except Exception as e:
        logerror('kitchen_utils::unpackboot_recovery ',e,1)
        

def unpackBootRecoveryfile(thefile):
    
    try:
        go_on = 0
        with open(thefile,'r') as f:
            check = f.read(8)
            if check == 'ANDROID!':
                go_on=1
            
                kernel = makeimage('Kernel',f)
                ramdisk = makeimage('Ramdisk',f)
                sramdisk = makeimage('Second Ramdisk',f)
                baseaddress = getint(f.read(4))
                pagesize = getint(f.read(4))
                kernel.setpagesize(pagesize)
                kernel.Offset = pagesize
                ramdisk.Offset = kernel.NextPageStart()
                sramdisk.Offset = ramdisk.NextPageStart()     
     
        if go_on ==1:
            kernel.writeimage(thefile,thefile + '-kernel')
            ramdisk.writeimage(thefile,thefile + '-ramdisk.gz')
            if sramdisk.Size != 0:
                sramdisk.writeimage(thefile,thefile + '-sramdisk.gz')

    except Exception as e:
        logerror('kitchen_utils::unpackBootRecoveryfile ',e,1)
                          
        
def makeimage(iname,f):
    try:
        s = getint(f.read(4))
        a = getint(f.read(4))       
        return part(iname,s,a) 
    except Exception as e:
        logerror('kitchen_utils::makeimage ',e,1)

def getint(data):
    return struct.unpack('i',data)[0]         

    
class part:
    _pagesize = 0
    
    def __init__(self,name,size,offset):
        try:
            self.Name = name.strip()
            self.Size = size
            self.Offset = offset
            part._pagesize = 0
        except Exception as e:
            logerror('kitchen_utils::part::__init__ ',e,1)
        
 
    def NextPageStart(self):
        try:
            return self.getpages() * part._pagesize + self.Offset
        except Exception as e:
            logerror('kitchen_utils::part::NextPageStart ',e,1)
            
            
    
    def getpages(self):
        try:
            return int((self.Size + part._pagesize - 1) / part._pagesize)
        except Exception as e:
            logerror('kitchen_utils::part::getpages ',e,1)
        
        
        
    def setpagesize(self,pgsize):
        try:
            part._pagesize = pgsize
        except Exception as e:
            logerror('kitchen_utils::part::setpagesize ',e,1)
        
        
    def writeimage(self,sourcefile,imagename):
        try:
            with open(sourcefile,'r') as s:
                print 'write file starting at ' + str(self.Offset)
                print 'size ' + str(self.Size)
                discard = s.read(self.Offset)
                buff = s.read(self.Size)
                print len(buff)
                with open(imagename,'w') as w:
                    w.write(buff)
        except Exception as e:
            logerror('kitchen_utils::part::writeimage ',e,1)
        
            
    def __str__(self):
        try:
            return self.Name + ': ' + str(self.Size) + ' ' + hex(self.Size) + ' ' + str(self.Offset)
        except Exception as e:
            logerror('kitchen_utils::part::__str__ ',e,1)
            
                
        
