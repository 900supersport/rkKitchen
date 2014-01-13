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
import shutil

#900supersport imports
import KitchenConfig
import rominfo
#import boot


from boot import brand_boot, initrc_mount_system_rw,addpreinstall, addinitd_support,unpackboot , finalise_boot  
from kitchenUI import header, pprint, mymenu
from utils import CheckMakeFolders, finalisefilesystemimage, mountfileasfilesystem, CheckMakeFoldersRoot, apply_sed, checkfsimage, logerror,zipfolder
from kitchen_utils import browse,removefiles,deployfiles,movefiles,copyfilesworker

from parameter import parse_parameter,parameter_menu, repairparams
from system import mountsystem, extendBuildprop, finalisesystem, growsystem, shrinksystem, makebusyboxlinks, resizerequired, systemmenu

from boot import bootmenu
from recovery import recoverymenu
from kernel import kernel_menu, getkerneldata
from flash import flash_menu
from rkunpack import rkunpack

#    try:
#        
#    except Exception as e:
#        logerror('rkmainmenu::mountsystem ',e,1)
#        raise
        
def rkmainmenu():
    '''Main menu for interaction with user
    
    This is a version 1 menu this needs to inspect the state of the current 
    working ROM and offer options as appropriate'''
    try:
        
        main_menu = dict([
            ('a1', 'Pick up img and create locations'), 
            ('b2', 'Clean, brand and root system and boot images'), 
            ('c3', 'Make ROM kits'),  
            ('d4', 'Clean workspace (removes working files)'), 
            #('f5', 'Wipe workspace, and unpacked'),
            ('g=', '='), 
            ('hb', 'boot menu'),
            ('ir', 'recovery menu'),
            ('js', 'system menu'),
            ('kk', 'kernel menu'),
            ('lp', 'parameter menu'),
            ('mf', 'flash menu'),
            #('ng', 'graphics'),
            ('p=', '='),
            ('qw', 'broWse'),
            ('t=', '='), 
            ('yx', 'eXit'), 
            ('z=', '=')
            ])
            
        choice = mymenu(
                    main_menu
                    ,'Enter selection :'
                    ,checkvalid = True)
        
        if choice in ('1'):
            setworkingROM()
        elif choice in ('2'):
            cleanroot()
        elif choice in ('3'):
            makeROMkits()
        elif choice in ('4'):
            cleanworkspace()
        #elif choice in ('5'):
        #    wipeworkspace()
        elif choice in ('b','B'):
            bootmenu()
        elif choice in ('s','S'):
            systemmenu()
        elif choice in ('r','R'):
            recoverymenu()
        elif choice in ('p','P'):
            parameter_menu()
        elif choice in ('f','F'):
            flash_menu()
        elif choice in ('r','R'):
            repairparams()
        elif choice in ('k','K'):
            kernel_menu()
        elif choice in ('W','w'):
            browse('')
        elif choice in ('x','X'):
            pprint('=')
            pprint('Exiting')
            pprint('=')
            
        if choice not in ('x', 'X'):
            rkmainmenu()
        
    except Exception as e:
        logerror('rkmainmenu::menu ',e,1)
        

def wipeworkspace():
    cleanworkspace()
    
    
def cleanworkspace():
    try:
        cont = 'Y'
        rn = rominfo.rominfo.romname
        rimg = rominfo.rominfo.romimgfilename
        
        src = os.path.join('sources',rn,rimg)
        dst = rimg
        
        #retrieve original img file
        if os.path.isfile(src):
            os.system('mv ' + src + ' ' + dst)
        else:
            cont = raw_input('No ROM image found \n' + src + '\n\nContinue Y/N:')
        
        #retrieve and archive any pulled images    
        if cont in ('Y', 'y'):
            zipfolder('read','ReadImages.zip')
            zipfolder('localdeploy','localdeploy.zip')
            os.system('sudo rm -rf working')
            shutil.rmtree('localdeploy')
            shutil.rmtree('sources')
            shutil.rmtree('read')
         
        rominfo.rominfo.romname = 'un-initialised'   
    except Exception as e:
        logerror('rkmainmenu::recursive_zip ',e,1)
        
        
def makeROMkits():
    '''make ROM kits based on current templates
   
    This is a run once process
'''
    try:
        src = os.path.join(KitchenConfig.KitchenConfig.KitchenPath, 'ROMtemplates/')
        dst = 'ROMKits/'
        pprint ('Copying from ' + src + ' to ' + dst)
        
        shutil.copytree(src,dst)
        pprint ('Adding images to ROM Kits')
        pcfilesrc = os.path.join(KitchenConfig.KitchenConfig.KitchenPath,'processcontrol/populateROMkits')
        copyfilesworker(pcfilesrc,'',0,verbose = 1)
        
        src = 'CWMROMKit.zip'
        tgt = os.path.join(dst,rominfo.rominfo.romname.strip() + '_' + src)
        src = os.path.join(dst,src)
        os.system('mv ' + src + ' ' + tgt)
        
        src = 'ROMKit.zip'
        tgt = os.path.join(dst,rominfo.rominfo.romname.strip() + '_' + src)
        src = os.path.join(dst,src)
        os.system('mv ' + src + ' ' + tgt)
    except Exception as e:
        logerror('rkmainmenu::makeROMkits ',e,1)

        
def setworkingROM():
    '''get an image and start the ROM kitchen process on it
    
    prompt for a rom image and load it into the kitchen
    
    Create a folder in the sources hierarchy move the image file there,
    unpack it and copy the extracted img and parameters file to the working 
    folder ready for cooking.
    
    instantiate and pickle a rominfo class to persist the ROM information
    '''
    
    logging.debug('Start setworkingROM')
    
    try:
        getROMFile()
        unpackROM()
        copyImages()
        saveromdata()  
        getkerneldata()  
        promptLocalDeploy()
    except Exception as e:
        logerror('rkmainmenu::setworkingROM ',e,1)

         
def promptLocalDeploy():   
    '''Promt the user to add any prepared files to the localdeploy folder
    '''
    try:
        pprint('=')
        pprint(' ')
        pprint(' ')
        pprint('Now put any local resources in localdeploy')
        pprint(' ')
        pprint(' ')
        pprint('=')
        time.sleep(5)
    except Exception as e:
        logerror('kitchen_utils::promptLocalDeploy ',e,1)
        
        
def getROMFile(): 
    '''prompt for a rom image and move it into the sources folder
    '''
    
    header();
    filepath = raw_input('Please enter file name:');
    pprint(' ')
    pprint('=')

    #remove any trailing whitespace or single quotes
    filepath = filepath.rstrip()
    filepath = filepath.strip("'")
  
    rominfo.rominfo.setROMimgFilename(os.path.basename(filepath))
    
    CheckMakeFolders([KitchenConfig.KitchenConfig.SourceROMUnpackedLoc()]); 
    
    try:
        shutil.move(filepath, KitchenConfig.KitchenConfig.SourceROMLoc() + '/')
    except IOError as e:
        logerror('rkmainmenu::getROMFile IOError',e,1)
    except NameError as e:
        logerror('rkmainmenu::getROMFile NameError',e,1)
       

def unpackROM():
    '''unpack the collected ROM image
    '''
    
    try:
        tcwd = os.getcwd()
        os.chdir(KitchenConfig.KitchenConfig.SourceROMUnpackedLoc())
        
        image = os.path.join('../' , rominfo.rominfo.romimgfilename)
        if image.find(' ') > 0:
            image = "'" + image + "'"
        logging.debug('rkunpack ' + image)
        rkunpack(image)
        #now fix bad parameter file if ends (use rather than (user)
        testcorrectparameter()
        
        #os.system( 'rkunpack ' + image )
        os.chdir(tcwd)
        
    except Exception as e:
        os.chdir(tcwd)
              
        logerror('rkmainmenu::getROMFile rkunpack fails ',e,0 )
        #now if this does not work try rkunpack
        try:
            os.system( 'unpack_all.sh ' 
                + os.path.join(KitchenConfig.KitchenConfig.SourceROMLoc(), rominfo.rominfo.romimgfilename) + ' ' 
                + KitchenConfig.KitchenConfig.SourceROMUnpackedLoc())
        except Exception as e:
            logerror('rkmainmenu::unpackROM unpack_all.sh',e,1)
 
 
def testcorrectparameter():
    with open('parameter','r') as f:
        buf = f.read()
        
    if buf[-4:] == '(use':
        with open('parameter','w') as f:
            f.write(buf + 'r)')
             
    
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
        
            
        for file in glob.glob(os.path.join(KitchenConfig.KitchenConfig.SourceROMUnpackedLoc(),'*.bin')):
            print file
            shutil.copy(file,'working')

        rominfo.rominfo.originalsystemsize = os.stat('working/system.img').st_size
        
    except Exception as e:
        logerror('rkmainmenu::copyImages ',e,1)


def saveromdata():
    '''save the rom data to the rominfo
    '''
    try: 
        parse_parameter()
    except Exception as e:
        logerror('rkmainmenu::saveromdata ',e,1)      
        
####################################################################
def cleanroot():
    '''clean and root system.img
    
    900supersport 1.1
    *   debloat
    *   root, xml permissions market fix and busybox by deploy files (global)
    *   branding by deploy files (Local)
    *   addition of busybox synbolic links
    *   build.prop update for language and region
    '''
    kc = KitchenConfig.KitchenConfig
    try:

        header(); 
        pprint('=')
        pprint('system.img')
        pprint('=')
        pprint('De-bloat')
        pprint('=')

        mountsystem()
        removefiles(os.path.join(kc.KitchenPath, 'processcontrol/debloat'),'working/mntsystem/') 

        growsystem()
        mountsystem()

        pprint('=')
        pprint('= rooting the Cube now')
        pprint('=')
        pprint('= add Busybox for init.d')
        pprint('=')

        movefiles(os.path.join(kc.KitchenPath, 'processcontrol/movepreinstall'))
        deployfiles(os.path.join(kc.KitchenPath, 'processcontrol/deploy'),'working/mntsystem',0)
        
        makebusyboxlinks(os.path.join(kc.KitchenPath, 'processcontrol/makelinks'))
        CheckMakeFoldersRoot(['working/mntsystem/etc/init.d'])

        pprint('=')
        pprint('make english')
        pprint('=')

        os.system('sudo cp working/mntsystem/build.prop working/removed')       

        apply_sed(os.path.join(kc.KitchenPath, 'processcontrol/buildprop_makeenglish')
            ,'working/mntsystem/build.prop'
            ,0)
        
        extendBuildprop(0)

        if resizerequired == -1:
            shrinksystem()
            mountsystem()
            
        #open nautilus for review
        os.system('sudo ' + kc.browser + ' working/mntsystem/')   
        finalisesystem()
        checkfsimage('working/system.img')
        
        #boot stuff
        unpackboot() 
        initrc_mount_system_rw(0)
        addinitd_support(0)
        addpreinstall(1)
        brand_boot(1)
        finalise_boot()       
            
    except Exception as e:
        logerror('rkmainmenu::cleanroot ' ,e,1)
        
