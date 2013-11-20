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
import pickle
import logging
import traceback
import zipfile

#    try:
#        
#    except Exception as e:
#        logerror('utils::mountsystem ' , e, 1)
#        

def zipfolder(sourcefolder,zipfilename):
    '''creates a zipfolder containing as an archive of sourcefolder
    
    if there are no files to be archived then the zip will be removed
    '''
    try:
        if os.path.isfile(zipfilename):
            mode = 'a'
        else:
            mode = 'w'
            
        zf = zipfile.ZipFile(zipfilename,mode)
        hasdata = recursive_zip(zf,sourcefolder)
        zf.close()
        if hasdata == 0 and mode =='w' :
            os.system(zipfilename)

    except Exception as e:
        logerror('utils::zipfolder ',e,1)

def recursive_zip(zipf, directory, folder = ""):
    try:
        append = 0
        for item in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, item)):
                zipf.write(os.path.join(directory, item), os.path.join(folder, item))
                append = 1
            elif os.path.isdir(os.path.join(directory, item)):
                if recursive_zip(zipf, os.path.join(directory, item), os.path.join(folder, item)) == 1:
                    append = 1
        return append
        
    except Exception as e:
        logerror('utils::recursive_zip ',e,1)


def GetCWD():
    return os.getcwd()

def CheckMakeFolders(folderlist):
    '''check the existance of and make any missing folders in the input list
    '''
    try:
        for dp in folderlist:
            CheckMakeFolderW(dp,0)
    except Exception as e:
        logerror('utils::CheckMakeFolders ' , e, 1)
        


def CheckMakeFoldersRoot(folderlist):
    '''check the existance of and make any missing folders as root in the input list
    '''
    try:
        for dp in folderlist:
            CheckMakeFolderW(dp,1)
    except Exception as e:
        logerror('utils::CheckMakeFoldersRoot ' , e, 1)
        
        
        
def CheckMakeFolder(dirpath):
    '''Check for existance of the folder and create
    
    if the folder specified by dirpath does not exist then create it.
    NB if recursion used if a a nested folder specified so all 
       folders in the path hierarchy and checked and created'''
    try:
        CheckMakeFolderW(dirpath,0)
    except Exception as e:
        logerror('utils::CheckMakeFolder ' , e, 1)
                
        

def CheckMakeFolderW(dirpath,asroot):
    '''Check for existance of the folder and create as root if specified
    
    if the folder specified by dirpath does not exist then create it.
    NB if recursion used if a a nested folder specified so all 
       folders in the path hierarchy and checked and created'''
    
    logging.debug('CheckMakeFolder start :' + dirpath)   
    
    try:
        if not os.path.isdir(dirpath):
            logging.debug('Making Folder :' + dirpath)
            logging.debug('as root :' + str(asroot))
            if asroot ==1:
                rt,pt = os.path.split(dirpath)
                if len(rt)>0:
                    logging.info(rt)
                    CheckMakeFolderW(rt,asroot)
                logging.info(  'sudo mkdir ' + pt)  
                os.system('sudo mkdir ' + dirpath)
            else:
                logging.debug('making with os.makedirs ' + dirpath)
                os.makedirs(dirpath + '/')
            logging.debug('Made Folder :' + dirpath)
    except Exception as e:
        logerror('utils::CheckMakeFolderW ' , e, 1)
         


def QueryPickleLoad(classvar, filepath):
    '''load a class from a pickle file
    '''
    
    try:
        logging.debug('Start QueryPickleLoad')
        logging.debug('Filepath :' + filepath)
        if os.path.exists(filepath):
            logging.debug('file exists')
            with open(filepath,'r') as f:
                logging.debug('file opened')
                classvar = pickle.load(f)
                logging.debug('file read')
        else:
            logging.info('utils::QueryPickleLoad Filepath not found :' + filepath)
            #raise IOError
    except Exception as e:
        logerror('utils::QueryPickleLoad ' , e, 1)
        
    finally:
        logging.debug('End QueryPickleLoad')
        return classvar
        
def PickleIt(classvar, filepath):
    '''Pickle a class to a file
    '''
    try:
        with open(filepath,'w') as f:
            pickle.dump(classvar,f)

    except IOError as e:
        print "I/O error({0}): {1}"#.format(e.errno, e.strerror)       
    except Exception as e:
        logerror('utils::PickleIt ' , e, 1)
                
    
def apply_sed(sedfilepath,applytopath,openforreview):
    '''apply the sed statements from file sedfilepath to the file applytopath'''
    try:
        path =os.path.expanduser(sedfilepath) 
        with open(path,'r') as f:
            for line in f:
                cl = line.strip();
                args = cl.split(',')
                if cl[:1] <> '#' and len(cl) > 0:
                    logging.debug( 'sudo sed -i ' + cl + ' ' + applytopath )
                    os.system('sudo sed -i ' + cl + ' ' + applytopath )
        
        if openforreview ==1:            
            os.system('sudo gedit ' + applytopath)
    except Exception as e:
        logerror('utils::apply_sed ' , e, 1)
            


def umount(mountpoint):
    '''unmount the specified filesystem'''
    try:
        systemstring = 'sudo umount ' + mountpoint
        os.system(systemstring)
    except Exception as e:
        logerror('utils::umount ' , e, 1)
         
            

def finalisefilesystemimage(mount, image):
    '''unmount and check a mounted filebased filesystem'''
    try:
        umount(mount)
        checkfsimage(image) 
    except Exception as e:
        logerror('utils::finalisefilesystemimage ' , e, 1)
             

def mountfileasfilesystem(mountfile, filesystemtype, mountpoint):    
    '''mount a files system to a mount point of the specifie type'''
    logging.debug('Start mountfileasfilesystem')
    try:
        CheckMakeFolder(mountpoint)
        systemstring = 'sudo mount -t ' + filesystemtype + ' -o loop ' + mountfile + ' ' + mountpoint
        os.system(systemstring)
    except Exception as e:
        
        logerror('utils::mountfileasfilesystem ' , e, 1)
              
        
    logging.debug('End mountfileasfilesystem')
    
    
def checkfsimage(image): 
    '''call e2fscheck on a file based filesystem'''   
    os.system('sudo e2fsck -y -v ' + image)                 
    


def logerror(errortext, myerror, raiseit):
    try:
        err = traceback.format_exc()
        logging.debug( 'bm' + err + 'bm')
        logging.error(errortext)
        logging.error(myerror)
        discard = myerror.handled
    except AttributeError as ae:
        logging.error(err)
        myerror.handled = 1  
    finally: 
        if raiseit == 1:    
            raise myerror
            
