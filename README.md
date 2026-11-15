# TWRP for Xiaodu G16 Pro / XDH-25-B3 (`xps10e`)

Unofficial TWRP 3.3.x device tree, built on GitHub Actions against the
`minimal-manifest-twrp/platform_manifest_twrp_omni` **twrp-9.0** branch.

## Device facts (extracted from the stock `recovery.img`)

| Item | Value |
|---|---|
| Marketing name | 小度 G16 Pro (Xiaodu G16 Pro) |
| Model | XDH-25-B3 |
| Device codename | `xps10e` |
| SoC | MediaTek **MT6765** (Helio P35 / G35) |
| Arch | arm64-v8a (+ armeabi-v7a) |
| Android | **9 / SDK 28** (P, treble, system-as-root) |
| Partition scheme | **A-only** (no A/B slots) |
| Recovery partition | 32 MiB (0x2000000) |
| Boot header | **v1**, page size 2048, kernel `Image.gz` |
| Kernel cmdline | `bootopt=64S3,32N2,64N2 buildvariant=user` |
| Kernel base | `0x40080000` (base `0x40000000`, kernel offset `0x80000`, ramdisk offset `0x11b00000`, tags offset `0x7880000`) |
| Display | 10.1" **1920x1200**, density 320, `ro.sf.hwrotation=90` |
| Userdata | ext4 + FBE (`aes-256-cts`) |

## Layout

```
device/xiaodu/xps10e/
├── Android.mk
├── AndroidProducts.mk
├── BoardConfig.mk
├── device.mk
├── omni_xps10e.mk
├── recovery.fstab
├── vendorsetup.sh
└── prebuilt/
    ├── Image.gz              # stock kernel, taken from recovery.img
    ├── recovery_dtbo.img     # stock recovery_dtbo (DTBO magic d7b7ab1e)
    └── init.recovery.mt6765.rc
```

## Building

Push to `main` or run the *Build TWRP (xps10e)* workflow manually.
This is **not** source-compiled AOSP: the MediaTek BSP kernel is unavailable, so the
stock `Image.gz` + `recovery_dtbo` are reused as prebuilts and only the recovery
ramdisk is built from `twrp-9.0`.

## Flashing

A-only device with a dedicated recovery partition:

```bash
# try without touching anything
fastboot boot recovery.img

# persist
fastboot flash recovery recovery.img
```

Or through BROM with mtkclient (works even without fastboot):
```bash
MtkClient w recovery recovery.img
```

## Known limitations

- **/data cannot be decrypted** — `TW_INCLUDE_CRYPTO` is off, the vendor keymaster
  blob for this device is not usable outside the stock recovery. Format data instead.
- Touch, display rotation and USB-ADB need to be verified on real hardware; the
  first build is a bring-up build.

## Credits

Stock kernel/DTBO © Baidu / Xiaodu. TWRP © Team Win Recovery Project.
