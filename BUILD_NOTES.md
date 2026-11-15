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
