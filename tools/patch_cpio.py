#!/usr/bin/env python3
"""Patch one file inside a gzip'd cpio (newc) ramdisk, preserving every other
entry's metadata byte-for-byte.

Packing from the extracted directory on Windows would lose permissions,
symlink targets and inode numbers, so instead we re-serialize the *original*
archive and only swap the payload of the file we care about.

usage: patch_cpio.py in.gz out.gz init.rc append.txt
"""
import gzip
import io
import struct
import sys

MAGICS = (b"070701", b"070702")
HDR = 110


def parse(cpio):
    out = []
    pos = 0
    while pos + HDR <= len(cpio):
        magic = cpio[pos:pos + 6]
        if magic not in MAGICS:
            raise SystemExit(f"bad cpio magic at {pos}: {magic!r}")
        f = [int(cpio[pos + 6 + i * 8: pos + 14 + i * 8], 16) for i in range(13)]
        (ino, mode, uid, gid, nlink, mtime, filesize,
         devmajor, devminor, rdevmajor, rdevminor, namesize, check) = f
        name_start = pos + HDR
        name = cpio[name_start:name_start + namesize - 1].decode("utf-8", "surrogateescape")
        data_start = name_start + namesize
        data_start = (data_start + 3) & ~3
        data = cpio[data_start:data_start + filesize]
        next_pos = (data_start + filesize + 3) & ~3
        out.append(dict(magic=magic, ino=ino, mode=mode, uid=uid, gid=gid,
                        nlink=nlink, mtime=mtime, devmajor=devmajor,
                        devminor=devminor, rdevmajor=rdevmajor,
                        rdevminor=rdevminor, check=check,
                        name=name, data=data))
        pos = next_pos
        if name == "TRAILER!!!":
            break
    return out


def build(entries):
    out = io.BytesIO()
    for e in entries:
        data = e["data"]
        name = e["name"].encode("utf-8", "surrogateescape")
        magic = e["magic"] if e["magic"] in MAGICS else b"070701"
        out.write(magic)
        out.write(b"".join(b"%08X" % v for v in (
            e["ino"], e["mode"], e["uid"], e["gid"], e["nlink"], e["mtime"],
            len(data), e["devmajor"], e["devminor"], e["rdevmajor"],
            e["rdevminor"], len(name) + 1, e["check"])))
        out.write(name + b"\0")
        pad = (-(HDR + len(name) + 1)) % 4
        out.write(b"\0" * pad)
        out.write(data)
        out.write(b"\0" * ((-len(data)) % 4))
    # cpio wants the archive padded to 512 bytes
    out.write(b"\0" * ((-out.tell()) % 512))
    return out.getvalue()


def main():
    src, dst, target, append_file = sys.argv[1:5]
    cpio = gzip.decompress(open(src, "rb").read())
    entries = parse(cpio)
    print(f"parsed {len(entries)} entries from {src} ({len(cpio)} bytes cpio)")

    found = None
    for e in entries:
        if e["name"].lstrip("./") == target.lstrip("./"):
            found = e
            break
    if found is None:
        raise SystemExit(f"{target} not found in ramdisk")

    old = found["data"]
    extra = open(append_file, "rb").read()
    if extra.strip() not in old:
        found["data"] = old + (b"" if old.endswith(b"\n") else b"\n") + extra
    print(f"{target}: {len(old)} -> {len(found['data'])} bytes")

    new_cpio = build(entries)
    # verify the round trip
    check = parse(new_cpio)
    assert len(check) == len(entries), (len(check), len(entries))
    for a, b in zip(entries, check):
        assert a["name"] == b["name"], (a["name"], b["name"])
        assert a["data"] == b["data"], a["name"]
        assert a["mode"] == b["mode"] and a["ino"] == b["ino"], a["name"]
    print("round-trip verification OK")

    blob = gzip.compress(new_cpio, 6, mtime=0)
    open(dst, "wb").write(blob)
    print(f"wrote {dst}: {len(blob)} bytes gz, {len(new_cpio)} bytes cpio")


if __name__ == "__main__":
    main()
