#!/usr/bin/env python3
"""Rebuild an AOSP boot/recovery image (header v1 + recovery_dtbo) using an
explicit header template taken from a stock image.

The TWRP build system ignored our BOARD_KERNEL_OFFSET / RAMDISK_OFFSET /
TAGS_OFFSET and BOARD_BOOT_HEADER_VERSION, producing a header-v0 image with
default addresses (which would not boot on MTK).  Rather than fight the
makefiles, we keep the freshly built kernel+ramdisk payload and repack it with
exactly the header fields the stock image used.
"""
import argparse
import hashlib
import os
import struct

MAGIC = b"ANDROID!"


def parse(path):
    with open(path, "rb") as f:
        hdr = f.read(4096)
    if hdr[:8] != MAGIC:
        raise SystemExit(f"{path}: bad magic {hdr[:8]!r}")
    f = {}
    (f["kernel_size"], f["kernel_addr"], f["ramdisk_size"], f["ramdisk_addr"],
     f["second_size"], f["second_addr"], f["tags_addr"], f["page_size"],
     f["header_version"], f["os_version"]) = struct.unpack_from("<10I", hdr, 8)
    f["name"] = hdr[48:64]
    f["cmdline"] = hdr[64:576]
    f["extra_cmdline"] = hdr[608:1632]
    (f["dtbo_size"], f["dtbo_offset"],
     f["header_size"]) = struct.unpack_from("<IQI", hdr, 1632)
    return f


def page_align(n, page):
    return (n + page - 1) // page * page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template", help="stock image used as header template")
    ap.add_argument("payload", help="built image to take kernel+ramdisk from")
    ap.add_argument("output")
    a = ap.parse_args()

    tpl = parse(a.template)
    src = parse(a.payload)
    page = tpl["page_size"]
    if src["page_size"] != page:
        raise SystemExit("page size mismatch")

    with open(a.payload, "rb") as f:
        f.seek(page)
        kernel = f.read(src["kernel_size"])
        f.seek(page_align(page + src["kernel_size"], page))
        ramdisk = f.read(src["ramdisk_size"])
    if len(kernel) != tpl["kernel_size"]:
        raise SystemExit(f"kernel size {len(kernel)} != stock {tpl['kernel_size']}")
    if ramdisk[:2] != b"\x1f\x8b":
        raise SystemExit("ramdisk is not gzip, refusing")

    dtbo = b""
    if tpl["dtbo_size"]:
        with open(a.template, "rb") as f:
            f.seek(tpl["dtbo_offset"])
            dtbo = f.read(tpl["dtbo_size"])
        if len(dtbo) != tpl["dtbo_size"]:
            raise SystemExit("short dtbo read")

    dtbo_offset = page_align(page + len(kernel), page) + page_align(len(ramdisk), page)

    # ---- header ----
    hdr = bytearray(tpl["header_size"] if tpl["header_size"] else 1648)
    hdr[0:8] = MAGIC
    struct.pack_into("<10I", hdr, 8,
                     len(kernel), tpl["kernel_addr"],
                     len(ramdisk), tpl["ramdisk_addr"],
                     0, tpl["second_addr"],
                     tpl["tags_addr"], page,
                     tpl["header_version"], tpl["os_version"])
    hdr[48:64] = tpl["name"]
    hdr[64:576] = tpl["cmdline"]
    hdr[608:1632] = tpl["extra_cmdline"]
    struct.pack_into("<IQI", hdr, 1632, len(dtbo), dtbo_offset if dtbo else 0,
                     len(hdr))

    # ---- image id (sha1 over payloads) ----
    sha = hashlib.sha1()
    for blob in (kernel, ramdisk, b"", dtbo):
        sha.update(blob)
        sha.update(struct.pack("<I", len(blob)))
    hdr[576:608] = sha.digest() + b"\0" * (32 - sha.digest_size)  # sha1 is 20B, field is 32B

    out = bytearray()
    out += hdr
    out += b"\0" * (page_align(len(hdr), page) - len(hdr))
    out += kernel
    out += b"\0" * (page_align(len(kernel), page) - len(kernel))
    out += ramdisk
    out += b"\0" * (page_align(len(ramdisk), page) - len(ramdisk))
    assert len(out) == dtbo_offset, (len(out), dtbo_offset)
    out += dtbo
    out += b"\0" * (page_align(len(out), page) - len(out))

    with open(a.output, "wb") as f:
        f.write(out)

    print(f"kernel      {len(kernel):>10}  @ 0x{tpl['kernel_addr']:08x}")
    print(f"ramdisk     {len(ramdisk):>10}  @ 0x{tpl['ramdisk_addr']:08x}")
    print(f"dtbo        {len(dtbo):>10}  @ {dtbo_offset}")
    print(f"header_ver  {tpl['header_version']:>10}")
    print(f"page_size   {page:>10}")
    print(f"image size  {len(out):>10}  (partition 33554432)")
    if len(out) > 33554432:
        raise SystemExit("image exceeds recovery partition!")
    print(f"sha256      {hashlib.sha256(out).hexdigest()}")
    print(f"written to  {a.output}")


if __name__ == "__main__":
    main()
