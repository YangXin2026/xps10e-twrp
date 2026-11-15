#!/usr/bin/env python3
"""Convert a raw framebuffer dump to PNG so we can actually see what TWRP renders."""
import sys, zlib, struct


def write_png(path, w, h, rows):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6))
    png += chunk(b"IEND", b"")
    open(path, "wb").write(png)


def main():
    src, out = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1200
    stride = int(sys.argv[5]) if len(sys.argv) > 5 else w * 4
    offset = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    order = sys.argv[7] if len(sys.argv) > 7 else "rgb"

    d = open(src, "rb").read()
    print("file", len(d), "-> w", w, "h", h, "stride", stride, "offset", offset, "order", order)
    if len(d) < offset + stride * h:
        print("!! data too short")
        return

    rows = []
    ri, gi, bi = (0, 1, 2) if order == "rgb" else (2, 1, 0)
    for y in range(h):
        base = offset + y * stride
        line = d[base:base + w * 4]
        row = bytearray(w * 3)
        row[0::3] = line[ri::4]
        row[1::3] = line[gi::4]
        row[2::3] = line[bi::4]
        rows.append(row)
    write_png(out, w, h, rows)
    print("wrote", out)


if __name__ == "__main__":
    main()
