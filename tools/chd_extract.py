#!/usr/bin/env python3
"""Extract files from a PS2 DVD CHD via libchdr (ISO9660). Usage: chd_extract.py <chd> <outdir> [names...]
With no names, extracts SYSTEM.CNF and the boot ELF."""
import ctypes, os, sys, struct
lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libchdr.so"))
class CHD:
    def __init__(s, path):
        s.h = ctypes.c_void_p()
        e = lib.chd_open(path.encode(), 1, None, ctypes.byref(s.h))
        if e: raise RuntimeError("chd_open err %d" % e)
        lib.chd_get_header.restype = ctypes.c_void_p
        hdr = lib.chd_get_header(s.h)
        # chd_header: length,version,flags,compression[4] (u32s) then hunkbytes,totalhunks (u32), logicalbytes,... 
        raw = ctypes.string_at(hdr, 64)
        s.hunkbytes, s.totalhunks = struct.unpack_from("<II", raw, 28)
        s.buf = ctypes.create_string_buffer(s.hunkbytes); s.cache = {}
    def hunk(s, n):
        if n not in s.cache:
            e = lib.chd_read(s.h, n, s.buf)
            if e: raise RuntimeError("chd_read err %d hunk %d" % (e, n))
            s.cache = {n: s.buf.raw}
        return s.cache[n]
    def read(s, off, ln):
        out = bytearray()
        while ln > 0:
            n, o = divmod(off, s.hunkbytes); c = min(ln, s.hunkbytes - o)
            out += s.hunk(n)[o:o+c]; off += c; ln -= c
        return bytes(out)
def walk(c, lba, size, prefix=""):
    d = c.read(lba*2048, size); i = 0
    while i < len(d):
        l = d[i]
        if l == 0: i = (i//2048+1)*2048; continue
        rec = d[i:i+l]; elba = struct.unpack_from("<I", rec, 2)[0]; esz = struct.unpack_from("<I", rec, 10)[0]
        flags = rec[25]; nl = rec[32]; name = rec[33:33+nl]
        if name not in (b"\0", b"\1"):
            nm = name.decode("latin1").split(";")[0]
            if flags & 2: yield from walk(c, elba, esz, prefix+nm+"/")
            else: yield prefix+nm, elba, esz
        i += l
if __name__ == "__main__":
    chd, outdir = sys.argv[1], sys.argv[2]; names = [n.upper() for n in sys.argv[3:]]
    c = CHD(chd); pvd = c.read(16*2048, 2048); assert pvd[1:6] == b"CD001", pvd[:8]
    rlba, rsz = struct.unpack_from("<I", pvd, 156+2)[0], struct.unpack_from("<I", pvd, 156+10)[0]
    files = {n.upper(): (l, s) for n, l, s in walk(c, rlba, rsz)}
    if not names:
        cnf = c.read(files["SYSTEM.CNF"][0]*2048, files["SYSTEM.CNF"][1]).decode("latin1"); print(cnf)
        boot = [x for x in cnf.splitlines() if x.upper().startswith("BOOT2")][0].split("cdrom0:\\")[1].split(";")[0]
        names = ["SYSTEM.CNF", boot.replace("\\", "/").upper()]
    os.makedirs(outdir, exist_ok=True)
    for n in names:
        l, s = files[n]; open(os.path.join(outdir, os.path.basename(n)), "wb").write(c.read(l*2048, s)); print("wrote", n, s)
