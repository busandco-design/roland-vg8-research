# TMP320P16PGL Internal-ROM Frontier — 2026-09-07

## Result

`NEW_ARCHITECTURE_LEVEL_SELF_READ_PRIMITIVE_IDENTIFIED__CONTROLLED_EXECUTION_PATH_OPEN__NO_ROM_DUMP__NO_E6`

## Why this matters

The VG-8 service documentation identifies IC23 as `TMP320P16PGL`, a custom DSP. The board wiring and package/pin functions strongly align it with the first-generation TI `TMS320C16` architecture, but the literal contents and any Roland customization beyond mask ROM remain unrecovered.

The current public project therefore treats standard C16 behavior as **family/architecture evidence**, not proof that every detail of the custom Roland part is identical.

## New architecture-level finding: TBLR can read program ROM

The first-generation TMS320 documentation defines `TBLR` (table read) as a three-cycle instruction that transfers a word from program memory into on-chip data RAM. The user guide explicitly states that the source program memory may be either **on-chip ROM or off-chip ROM/RAM**.

The C16 data sheet also lists `TBLR` in the instruction set and provides dedicated TBLR bus timing.

This changes the conceptual ROM-recovery problem:

> On a standard-compatible C16 core, the internal program ROM is not intrinsically opaque to software executing on the DSP; it is architecturally readable by `TBLR` while mapped.

The remaining problem is gaining a safe, controlled execution path that can issue TBLR against the internal-ROM address range and export the resulting data.

## Memory-mode facts and ambiguity

For the standard C16 family:

- MC/MP high selects microcomputer mode, mapping the 8K-word on-chip program ROM.
- MC/MP low selects microprocessor mode, making the program space external.
- The C16 has a 64K-word program address space and 8K words of on-chip program ROM.

The available C16 terminal description says the modes are defined by the **state** of MC/MP. Unlike the C14 section of the same family data sheet, the C16 timing section visible in the public data does not specify a dedicated MC/MP setup/hold timing around reset.

That absence is **not proof** that MC/MP can safely be switched dynamically during execution. A dynamic-mode-switch recovery technique remains a hypothesis until authoritative timing/behavior evidence or a controlled sacrificial test demonstrates it.

## Candidate recovery routes

### Route A — Existing internal-ROM diagnostic/read command

Search host/service behavior for a command that causes IC23 to table-read or export internal program memory.

Status: **OPEN / preferred non-invasive route**.

Existing VG firmware analysis has not found an arbitrary IC23 program-memory read command, but the newly established TBLR capability provides a more specific target for further diagnostic archaeology.

### Route B — Controlled external execution + internal-ROM remap

Conceptual sequence only:

1. obtain controlled code execution from external program memory;
2. execute from an address that remains external when the low ROM window is mapped;
3. map the on-chip ROM;
4. use TBLR to copy ROM words into data RAM;
5. export the data through an I/O path.

Critical unresolved dependencies:

- whether the custom TMP320P16PGL preserves standard C16 TBLR behavior;
- whether MC/MP can be changed safely while running;
- whether the external address region remains executable across the mode transition exactly as assumed;
- electrical accessibility of MC/MP on the VG-8 board;
- a safe way to load/execute the external program without damaging the device or corrupting other buses.

Status: **E5 hypothesis only; no hardware action authorized**.

### Route C — Development/emulation hardware

TI documentation shows source-debugger/EVM support for TMS320C16, but contemporary development support documentation also states that the older XDS/22 emulator supports C1x **except TMS320C16**. No public evidence recovered here shows a standard in-circuit emulator that can attach to the installed custom TMP320P16PGL and dump its mask ROM.

Status: **no practical installed-chip dump path identified**.

### Route D — Physical silicon/ROM imaging

Decapsulation and optical/e-beam ROM extraction remains a possible literal-ROM route if a suitable donor and expertise become available.

Status: **invasive; not a current project prerequisite**.

## What is already behaviorally recovered

The VG host-visible IC23 packet is substantially constrained:

- word `0x28`: low byte selects physical string 0–5;
- word `0x2A`: amplitude/envelope field with packet-reject behavior;
- word `0x2C`: pitch-period/state with invalid-pitch behavior.

Downstream host firmware reconstructs per-string pitch smoothing/stability, envelope/activity, attack, transitions, note coordinate, and bounded pitch-motion state.

The active-note CPU region makes zero calls into the recovered CSP PRAM/CRAM programming API, favoring a parallel IC23/IC22 hardware-side control route rather than per-note CPU DSP rewrites.

This remains a **behavioral substitute**, not a literal TMP320P16PGL emulator.

## Evidence boundary

No internal ROM bytes were recovered.
No hardware was driven or modified.
No dynamic MC/MP behavior was demonstrated.
No TBLR operation was observed on the custom Roland part.

The new finding is therefore a **high-value architecture-level recovery hypothesis**, not ROM recovery and not E6.

## Next safe work

1. Continue primary-document search for C16 MC/MP switching semantics and C16-specific development/emulator hardware.
2. Search VG host/service firmware for hidden IC23 commands whose observable behavior could correspond to table reads or memory diagnostics.
3. Build a minimal C16/TBLR proof-of-concept in an emulator or reference environment using only public architecture documentation.
4. Preserve a hardware test design separately, but do not execute it without explicit authorization, suitable hardware access, and electrical review.
