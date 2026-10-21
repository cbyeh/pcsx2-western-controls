#!/usr/bin/env python3
"""Check .pnach patches for overlapping memory writes.

usage: audit_pnach.py <patches dir> [PCSX2 resources/patches.zip]

Every [section] in every file for the same SERIAL_CRC is compared with every
other one (including PCSX2's bundled database patches if patches.zip is given).
Sections listed in MUTUALLY_EXCLUSIVE are expected to overlap (enable only one).
"""
import re, sys, glob, os, zipfile, itertools, collections

MUTUALLY_EXCLUSIVE = [{"Right Stick Camera", "Right Stick Camera (Inverted)"}]


def parse(text):
    secs = collections.OrderedDict()
    cur = None
    for raw in text.splitlines():
        ln = raw.split("//")[0].strip()
        m = re.match(r"\[(.+)\]$", ln)
        if m:
            cur = m.group(1)
            secs.setdefault(cur, set())
            continue
        m = re.match(r"patch=\d+,EE,([0-9a-fA-F]{8}),(\w+),([0-9a-fA-F]+)", ln)
        if not m:
            continue
        a, t = int(m.group(1), 16), m.group(2).lower()
        if t == "extended":
            code = a >> 28
            if code in (0xD, 0xE):  # conditionals: read only
                continue
            size = {0: 1, 1: 2, 2: 4}.get(code, 4)
        else:
            size = {"byte": 1, "short": 2, "word": 4, "double": 8}[t]
        addr = a & 0x01FFFFFF  # strip kseg/uncached mirror bits
        secs.setdefault(cur or "(unlabelled)", set()).update(range(addr, addr + size))
    return secs


def main():
    pdir = sys.argv[1]
    zpath = sys.argv[2] if len(sys.argv) > 2 else None
    games = collections.defaultdict(list)
    for f in glob.glob(os.path.join(pdir, "*.pnach")):
        key = "_".join(os.path.basename(f).split("_")[:2]).split(".")[0]
        for s, w in parse(open(f, encoding="utf-8", errors="replace").read()).items():
            games[key].append((os.path.basename(f), s, w))
    if zpath:
        z = zipfile.ZipFile(zpath)
        for key in list(games):
            name = key + ".pnach"
            if name in z.namelist():
                for s, w in parse(z.read(name).decode("utf-8", "replace")).items():
                    games[key].append(("patches.zip:" + name, s, w))
    bad = 0
    for key, secs in sorted(games.items()):
        print("==", key)
        for f, s, w in secs:
            print("   %-45s %-40s %4d bytes" % (f, s, len(w)))
        for (f1, s1, w1), (f2, s2, w2) in itertools.combinations(secs, 2):
            ov = w1 & w2
            if not ov:
                continue
            if any({s1, s2} <= g for g in MUTUALLY_EXCLUSIVE):
                print("   ok (mutually exclusive): %s <-> %s" % (s1, s2))
                continue
            bad += 1
            print("   CONFLICT: %s:%s <-> %s:%s at %s (%d bytes)" % (f1, s1, f2, s2, hex(min(ov)), len(ov)))
    print("conflicts:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
