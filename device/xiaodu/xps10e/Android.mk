LOCAL_PATH := $(call my-dir)

ifneq ($(filter xps10e,$(TARGET_DEVICE)),)
include $(call all-makefiles-under,$(LOCAL_PATH))
endif
