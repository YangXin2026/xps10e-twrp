# Build notes

## Result

- TWRP **3.7.0_9-0**, `twrp-9.0` minimal manifest, built on GitHub Actions
  inside an `ubuntu:20.04` container (AOSP 9 still needs python2).
- Kernel: **stock** `Image.gz` from the device's own `recovery.img`
  (9,633,336 bytes, sha256 `e434c1abecea9aa5...`), unchanged.
- Ramdisk: TWRP, gzip, 15,308,436 bytes.

## Why the CI image had to be repacked

`make recoveryimage` produced a **header v0** image using default addresses:
the TWRP/omni makefiles ignored `BOARD_KERNEL_OFFSET`, `BOARD_RAMDISK_OFFSET`,
`BOARD_TAGS_OFFSET` and `BOARD_BOOT_HEADER_VERSION`:

| field | stock (works) | CI output (wrong) |
|---|---|---|
| header_version | 1 | 0 |
| kernel_addr | 0x40080000 | 0x40000000 |
| ramdisk_addr | 0x51b00000 | 0x41000000 |
| tags_addr | 0x47880000 | 0x40008000 |
| recovery_dtbo_size | 80381 | 0 |

Booting that on MTK would hand the kernel to the wrong physical address.

Fix: `tools/repack_boot.py` keeps the freshly built kernel+ramdisk payload and
rebuilds the header byte-for-byte from the **stock image used as a template**,
re-appending the stock `recovery_dtbo` at a recomputed offset.
`tools/verify_img.py` diffs every header field against the stock image.

Verified output: every field matches the stock image except
`recovery_dtbo_offset`, which necessarily moves because the TWRP ramdisk is
3x larger than stock.

## Gotcha

`hdr[576:608] = sha.digest()` silently shortened the header by 12 bytes
(sha1 is 20 bytes, the id field is 32), shifting every later field. Pad it.

## Second fix: framebuffer orientation

TWRP booted (the AVB footer was the blocker) but the UI was stretched and
touch was unusable. Two separate causes, one root: **the kernel framebuffer is
the panel's native orientation**.

The LCM is a `nt35695B` in DSI command mode with a native 1200x1920 portrait
panel, mounted landscape. Android hides this with `ro.sf.hwrotation=90` (a
userspace rotation); TWRP does not implement that property, so it read a
**1200x1920** framebuffer and squeezed the 1920x1200 landscape theme into it:

```
framebuffer: 0 (1200 x 1920)
I:Scaling theme width 0.625000x and height 1.600000x
```

Touch reported 0..1920 x 0..1200, i.e. transposed against the framebuffer, so
taps landed in the wrong place and the UI felt dead.

Fix: rotate the mode at the kernel level **before** TWRP opens fb0, by adding
this to the ramdisk `init.rc`:

```
on early-init
    write /sys/class/graphics/fb0/rotate 90

on init
    write /sys/class/graphics/fb0/rotate 90
```

After that `modes` becomes `U:1920x1200p-0`, `framebuffer: 0 (1920 x 1200)`,
and no scaling line is logged at all — the theme renders 1:1.

`tools/patch_cpio.py` applies this by **re-serialising the original cpio**
rather than packing the extracted tree, so every other entry keeps its inode
number, mode, uid/gid and symlink target byte for byte. Round-trip verified
against all 3454 entries. Usage:

```
python3 tools/patch_cpio.py built_ramdisk.gz ramdisk_patched.gz init.rc append.txt
python3 tools/repack_boot.py stock_recovery.img ci_recovery.img out.img --ramdisk ramdisk_patched.gz
python3 tools/add_avb.py out.img out-avb.img --partition recovery --partition-size 33554432
```

`tools/fb2png.py` turns a raw `/dev/graphics/fb0` dump into a PNG so the
rendered UI can be inspected without a physical screen grab.
