#!/usr/bin/env python3
"""Tiny documentation-derived TMS320C1x TBLR/OUT proof model.

Purpose: demonstrate the *architectural possibility* of copying a program-memory
word into data RAM with TBLR and then exporting it with OUT. This is not a
TMP320P16PGL emulator and does not model timing, undocumented behavior, or VG-8
hardware.
"""
from dataclasses import dataclass, field

@dataclass
class C1xTblrModel:
    program: list[int]
    data: list[int] = field(default_factory=lambda: [0] * 256)
    acc: int = 0
    ports: dict[int, int] = field(default_factory=dict)

    def tblr(self, data_addr: int) -> None:
        """TBLR: program[low16(ACC)] -> data RAM."""
        src = self.acc & 0xFFFF
        if not (0 <= src < len(self.program)):
            raise IndexError(f"program address 0x{src:04X} is not mapped")
        self.data[data_addr & 0xFF] = self.program[src] & 0xFFFF

    def out(self, port: int, data_addr: int) -> None:
        """OUT: data RAM -> selected I/O port."""
        self.ports[port & 0x7] = self.data[data_addr & 0xFF] & 0xFFFF


def self_test() -> None:
    rom = [0] * 0x2000
    sentinels = {0x0000: 0x1357, 0x0123: 0xA55A, 0x1FFF: 0xC04D}
    for addr, word in sentinels.items():
        rom[addr] = word
    cpu = C1xTblrModel(rom)
    for i, (addr, expected) in enumerate(sentinels.items()):
        cpu.acc = addr
        cpu.tblr(i)
        cpu.out(i, i)
        assert cpu.data[i] == expected
        assert cpu.ports[i] == expected
    print("PASS: documented TBLR->data RAM->OUT path reproduces all synthetic ROM sentinels")
    print("BOUNDARY: standard C1x documentation model only; no TMP320P16PGL hardware claim")

if __name__ == "__main__":
    self_test()
