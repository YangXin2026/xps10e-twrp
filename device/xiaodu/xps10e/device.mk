#
# Device makefile for xps10e
#

LOCAL_PATH := device/xiaodu/xps10e

# Boot/board identification, mirrors the stock recovery's prop.default
PRODUCT_DEFAULT_PROPERTY_OVERRIDES += \
    ro.board.platform=mt6765 \
    ro.hardware=mt6765 \
    ro.mediatek.platform=MT6765 \
    ro.product.first_api_level=28 \
    ro.treble.enabled=true \
    ro.adb.secure=0 \
    ro.secure=0 \
    ro.debuggable=1 \
    persist.sys.usb.config=adb \
    ro.sf.lcd_density=320 \
    ro.zygote=zygote64_32 \
    persist.radio.multisim.config=dsds

# Extra files pushed into the recovery ramdisk
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/recovery.fstab:$(TARGET_COPY_OUT_RECOVERY)/root/etc/recovery.fstab

# MTK keeps a tiny init fragment that brings up the musb gadget for adb/ffs.
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilt/init.recovery.mt6765.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.mt6765.rc
