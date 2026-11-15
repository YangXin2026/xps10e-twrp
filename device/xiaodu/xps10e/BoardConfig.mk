#
# TWRP device tree for Xiaodu G16 Pro / XDH-25-B3 (xps10e)
# SoC: MediaTek MT6765 (Helio P35/G35)  |  Android 9 / SDK 28  |  A-only
#

DEVICE_PATH := device/xiaodu/xps10e

# Allow building without all AOSP deps present
ALLOW_MISSING_DEPENDENCIES := true

# ---------------------------------------------------------------- architecture
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := cortex-a53
TARGET_CPU_VARIANT_RUNTIME := cortex-a53

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := cortex-a53
TARGET_2ND_CPU_VARIANT_RUNTIME := cortex-a53

TARGET_BOARD_PLATFORM := mt6765
TARGET_BOOTLOADER_BOARD_NAME := mt6765
TARGET_NO_BOOTLOADER := true
TARGET_USES_64_BIT_BINDER := true

# ------------------------------------------------------------------- bootloader
TARGET_USES_UEFI := false

# ---------------------------------------------------------------------- kernel
# Values copied 1:1 from the stock recovery.img header (verified by unpacking it).
BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2 buildvariant=user
BOARD_KERNEL_BASE := 0x40000000
BOARD_KERNEL_OFFSET := 0x00080000
BOARD_RAMDISK_OFFSET := 0x11b00000
BOARD_TAGS_OFFSET := 0x07880000
BOARD_KERNEL_PAGESIZE := 2048

BOARD_KERNEL_IMAGE_NAME := Image.gz
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/Image.gz

# header v1 + separate recovery_dtbo (stock layout)
BOARD_BOOT_HEADER_VERSION := 1
BOARD_INCLUDE_RECOVERY_DTBO := true
BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/recovery_dtbo.img

# ------------------------------------------------------------------ partitions
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 33554432
BOARD_FLASH_BLOCK_SIZE := 131072

TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery.fstab
TARGET_RECOVERY_DEVICE_DIRS += $(DEVICE_PATH)
TARGET_RECOVERY_PIXEL_FORMAT := "ABGR_8888"
TARGET_USES_MKE2FS := true

BOARD_USES_MTK_HARDWARE := true
TARGET_OTA_ASSERT_DEVICE := xps10e,XDH-25-B3

# ---------------------------------------------------------------------- TWRP
TW_THEME := landscape_hdpi
TW_DEFAULT_LANGUAGE := zh_CN
TW_EXTRA_LANGUAGES := true
TW_USE_TOOLBOX := true
TW_INCLUDE_NTFS_3G := true
TW_MAX_BRIGHTNESS := 255
TW_DEFAULT_BRIGHTNESS := 180
TW_NO_SCREEN_BLANK := true
TW_SCREEN_BLANK_ON_BOOT := false
TW_USE_MODEL_HARDLINK_USER := noreplace

# Keep TWRP from trying to decrypt FBE data it has no keymaster for.
TW_INCLUDE_CRYPTO := false
TW_INCLUDE_FBE := false

# Debug helpers, useful while bringing the device up
TWRP_INCLUDE_LOGCAT := true
TARGET_USES_LOGD := true
