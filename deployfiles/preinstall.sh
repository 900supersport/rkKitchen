#!/system/bin/sh
# preinstall
if [ ! -e /data/.notfirstboot ]
then
    busybox touch /data/.notfirstboot
    
    if [ -e /system/preinstall/ ]
    then
        APKLIST=`ls /system/preinstall/*.apk`
        for INFILES in $APKLIST
        do
          pm install -r $INFILES
        done
    fi
    
    if [ -e /mnt/external_sd/autoinstall/ ]
    then
        APKLIST=`ls /mnt/external_sd/autoinstall/*.apk`
        for INFILES in $APKLIST
        do
            pm install -r $INFILES
        done
    fi

    if [ -e /system/preinstall/recovery.img ]
    then

        flash_image recovery /system/preinstall/recovery.img
        mount -o rw,remount /dev/block/mtdblock8 /system
        mv /system/preinstall/recovery.img /system/preinstall/recovery.done

        mount -o ro,remount /dev/block/mtdblock8 /system
    fi
fi
exit
