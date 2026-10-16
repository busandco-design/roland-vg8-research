#!/usr/bin/env python3
"""Reproduce issue #1 checks on locally supplied images; emits no ROM bytes.

Requires capstone, unicorn, and (with --updater) mido. No hardware access.
Pass the 384/512 KiB assembled images, or the retained 0x5FC00/0x7FD00
ordinary streams. Padding is accepted only when the resulting SHA-256 matches.
"""
import argparse
import hashlib
import io
import json
import random
import struct
import sys
import zipfile
from pathlib import Path

import capstone
import unicorn
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES


HASHES = {
    "v104": "396230b85affbc975c6bd39182d44862cae39f64fab7d23dfd7951ae8ead4866",
    "ex101": "c7045aaa10f3eaa020e64e045c4ba7497c4c093801d4f3d1c9d8ccf2ce617c12",
}
PATTERN = bytes.fromhex("b800108ec0")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(path, kind):
    raw = path.read_bytes()
    prefix, suffix = (0x400, 0) if kind == "v104" else (0x100, 0x200)
    ordinary_size = 0x5FC00 if kind == "v104" else 0x7FD00
    padded = len(raw) == ordinary_size
    image = bytes(prefix) + raw + bytes(suffix) if padded else raw
    if sha(image) != HASHES[kind]:
        raise ValueError(f"{kind}: assembled SHA-256 does not match issue #1")
    return image, {
        "input_name": path.name, "input_bytes": len(raw), "input_sha256": sha(raw),
        "zero_prefix_added": prefix if padded else 0,
        "zero_suffix_added": suffix if padded else 0,
        "assembled_bytes": len(image), "assembled_sha256": sha(image),
    }


def sites(data, pattern):
    found, start = [], 0
    while True:
        start = data.find(pattern, start)
        if start < 0:
            return found
        found.append(start)
        start += 1


def disassemble(image, start, end):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
    return [{"file_offset": hex(i.address), "instruction": i.mnemonic + " " + i.op_str}
            for i in md.disasm(image[start:end], start)]


def reconstruct_updater(path):
    import mido
    result, packets = bytearray(), 0
    with zipfile.ZipFile(path) as archive:
        for name in ("VG1.MID", "VG2.MID", "VG3.MID"):
            midi = mido.MidiFile(file=io.BytesIO(archive.read(name)))
            for track in midi.tracks:
                for event in track:
                    if event.type != "sysex":
                        continue
                    data = bytes(event.data)
                    if len(data) != 156 or data[:4] != bytes((0x41, 0x7F, 0x74, 0x12)):
                        continue
                    if sum(data[4:]) % 128:
                        raise ValueError("Roland DT1 checksum failed")
                    bits = "".join(f"{v:07b}" for v in data[8:-1])[:1024]
                    result.extend(int(bits[i:i+8], 2) for i in range(0, 1024, 8))
                    packets += 1
    if packets != 3064:
        raise ValueError(f"Expected 3064 ordinary packets, got {packets}")
    return bytes(result), {"archive_sha256": sha(path.read_bytes()),
                           "checksummed_packets": packets, "mido_version": str(mido.version_info)}


def expected_envelope(amplitude, scale):
    high = (amplitude * scale) >> 16
    if high >= 0x2000:
        return 0x7FFF
    curve = (0, 0x2000, 0x4000, 0x5000, 0x6000, 0x6800, 0x7000, 0x7800, 0x7FFF)
    segment, fraction = high >> 10, high & 0x3FF
    return curve[segment] + ((fraction * (curve[segment+1] - curve[segment])) >> 10)


def run_handler(image, index, amplitude, pitch, scale, compared_string, disabled):
    """Execute only the ordinary x86 body; stop before NEC-specific epilogue.

    RAM and packet input are synthetic. This is CPU data-flow verification,
    not interrupt timing, peripheral acknowledgement, or hardware validation.
    """
    uc = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_16)
    uc.mem_map(0, 0x110000)
    uc.mem_write(0x80000, image)
    uc.reg_write(UC_X86_REG_CS, 0x9FF7)
    uc.reg_write(UC_X86_REG_DS, 0x40)
    uc.reg_write(UC_X86_REG_ES, 0)
    pointers = struct.unpack_from("<6H", image, 0x2001C)
    for lane, ptr in enumerate(pointers):
        ring = 0x3000 + lane * 0x80
        uc.mem_write(0x400 + ptr, struct.pack("<4H", ring, ring, ring, ring + 0x80))
        uc.mem_write(0x400 + 0x2D2 + lane*2, struct.pack("<H", scale))
    uc.mem_write(0x400 + 0x1150, struct.pack("<H", compared_string))
    uc.mem_write(0x400 + 0x1448, bytes([disabled]))
    uc.mem_write(0x10028, struct.pack("<3H", index, amplitude, pitch))
    uc.emu_start(0x9FF83, 0xA0018, count=200)
    lane = index & 0xFF
    counts = [uc.mem_read(0x400 + ptr + 0x2C, 1)[0] for ptr in pointers]
    accepted = lane < 6 and amplitude & 0x8000 == 0 and disabled == 0
    expected_counts = [int(accepted and i == lane) for i in range(6)]
    assert counts == expected_counts, (index, amplitude, pitch, counts)
    record = None
    if accepted:
        record = struct.unpack("<2H", uc.mem_read(0x400 + 0x3004 + lane*0x80, 4))
        expected = (0xFFFF if pitch & 0x8000 else pitch, expected_envelope(amplitude, scale))
        assert record == expected, (record, expected)
    return {"counts": counts, "record": record}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v104", type=Path, required=True)
    parser.add_argument("--ex", type=Path, required=True)
    parser.add_argument("--updater", type=Path)
    args = parser.parse_args()
    old, old_meta = prepare(args.v104, "v104")
    ex, ex_meta = prepare(args.ex, "ex101")
    result = {"evidence_class": "E3", "hardware_tested": False,
              "python": sys.version.split()[0], "capstone": capstone.__version__,
              "unicorn": unicorn.__version__, "v104": old_meta, "ex101": ex_meta}
    if args.updater:
        rebuilt, metadata = reconstruct_updater(args.updater)
        assert bytes(0x400) + rebuilt == old
        result["updater_reconstruction"] = metadata | {"matches_retained_stream": True}
    expected_sites = ([0x19534, 0x19571], [0x1FE32, 0x1FE6F, 0x1FF83])
    for image, meta, expected in zip((old, ex), (old_meta, ex_meta), expected_sites):
        locations = sites(image, PATTERN)
        assert locations == expected, locations
        meta["signature_file_offsets"] = [hex(i) for i in locations]
        meta["signature_linear_addresses_at_base_80000"] = [hex(i+0x80000) for i in locations]
    # Presence/absence of this short EX read sequence is not a complete CFG proof.
    read_sequence = ex[0x1FF88:0x1FF9A]
    result["ex_word_read_sequence_matches"] = {
        "v104": [hex(i) for i in sites(old, read_sequence)],
        "ex101": [hex(i) for i in sites(ex, read_sequence)],
    }
    result["v104_drain_disassembly"] = disassemble(old, 0x19571, 0x1958F)
    far_calls = [i for i in range(len(old)-4) if old[i] == 0x9A
                 and struct.unpack_from("<H", old, i+1)[0]
                 + 16 * struct.unpack_from("<H", old, i+3)[0] == 0x99571]
    assert far_calls == [0x193E6, 0x193EB, 0x193F0]
    result["v104_direct_far_calls_to_drain_linear"] = [hex(i+0x80000) for i in far_calls]
    result["v104_additional_caller_disassembly"] = disassemble(old, 0x193E6, 0x193FA)
    result["ex_consumer_disassembly"] = disassemble(ex, 0x1FF83, 0x20018)
    result["ex_state_pointer_table"] = [hex(v) for v in struct.unpack_from("<6H", ex, 0x2001C)]
    result["ex_envelope_curve"] = [hex(v) for v in struct.unpack_from("<9H", ex, 0x20028)]
    cases = [(i, a, p, s, c, d) for i in (0, 5, 6, 0xAB00)
             for a in (0x80, 0x8000, 0x7FFF)
             for p in (0x80, 0x8000) for s in (0, 0xFFFF)
             for c in (0, 5) for d in (0, 1)]
    rng = random.Random(1)
    cases += [(rng.randrange(6), rng.randrange(0x8000), rng.randrange(0x10000),
               rng.randrange(0x10000), rng.randrange(6), 0) for _ in range(128)]
    for case in cases:
        run_handler(ex, *case)
    # Same packet accepted for both outcomes of the RAM 0x1150 comparison.
    assert run_handler(ex, 0, 0x1234, 0x5678, 0x4000, 0, 0) == run_handler(ex, 0, 0x1234, 0x5678, 0x4000, 5, 0)
    result["synthetic_handler_cases_passed"] = len(cases) + 2
    result["limitations"] = [
        "Signature search is not exhaustive control-flow or alias analysis.",
        "Unicorn runs the handler body with synthetic RAM; NEC interrupt entry/exit and peripheral side effects are excluded.",
        "Packet naming and physical device ownership remain architectural interpretations.",
    ]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
