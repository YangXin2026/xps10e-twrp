#!/usr/bin/env python3
"""Compare a built recovery image against the stock one (AOSP boot header v1)."""
import struct
import sys
import hashlib

MAGIC = b"ANDROID!"


def read_header(path):
    with open(path, "rb") as f:
        data = f.read(4096)
    if data[:8] != MAGIC:
        raise SystemExit(f"{path}: not an ANDROID boot image (magic={data[:8]!r})")
    h = {}
    (h["kernel_size"], h["kernel_addr"], h["ramdisk_size"], h["ramdisk_addr"],
     h["second_size"], h["second_addr"], h["tags_addr"], h["page_size"],
     h["header_version"], h["os_version"]) = struct.unpack_from("<10I", data, 8)
    h["name"] = data[48:64].rstrip(b"\0").decode("ascii", "replace")
    h["cmdline"] = data[64:576].rstrip(b"\0").decode("ascii", "replace")
    h["id"] = data[576:608]
    h["extra_cmdline"] = data[608:1632].rstrip(b"\0").decode("ascii", "replace")
    (h["recovery_dtbo_size"], h["recovery_dtbo_offset"],
     h["header_size"]) = struct.unpack_from("<IQI", data, 1632)
    (h["dtb_size"], h["dtb_addr"]) = struct.unpack_from("<IQ", data, 1648)
    return h, data


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main(stock, built):
    hs, ds = read_header(stock)
    hb, db = read_header(built)
    keys = ["page_size", "kernel_addr", "ramdisk_addr", "second_addr", "tags_addr",
            "header_version", "os_version", "name", "header_size",
            "recovery_dtbo_size", "recovery_dtbo_offset", "dtb_size", "dtb_addr"]
    print(f"{'field':22} {'stock':>14} {'built':>14}  match")
    print("-" * 66)
    ok = True
    for k in keys:
        a, b = hs[k], hb[k]
        same = a == b
        if not same:
            ok = False
        print(f"{k:22} {str(a):>14} {str(b):>14}  {'OK' if same else 'DIFF'}")
    print()
    for label, h in (("stock", hs), ("built", hb)):
        print(f"{label} cmdline: {h['cmdline']}")
    print()
    # kernel bytes
    for label, path, h in (("stock", stock, hs), ("built", built, hb)):
        with open(path, "rb") as f:
            f.seek(h["page_size"])
            kern = f.read(h["kernel_size"])
        print(f"{label} kernel: {h['kernel_size']} bytes sha256={sha(kern)}")
    print()
    print("HEADER COMPATIBLE" if ok else "HEADER MISMATCH -> device may not boot")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
