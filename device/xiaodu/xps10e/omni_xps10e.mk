#
# Product definition for xps10e (Xiaodu G16 Pro / XDH-25-B3)
#

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/embedded.mk)
$(call inherit-product, vendor/omni/config/common.mk)
$(call inherit-product, device/xiaodu/xps10e/device.mk)

PRODUCT_DEVICE := xps10e
PRODUCT_NAME := omni_xps10e
PRODUCT_BRAND := Xiaodu
PRODUCT_MODEL := XDH-25-B3
PRODUCT_MANUFACTURER := Xiaodu
