# Public Technical State — 2026-09-07

## Authority
`CP41_AUTHORITATIVE_E3_FACTORY_CORE_AND_EXACT_PRELOAD_TRANSACTION_EQUIVALENCE` remains authority; post-CP41 reconciliation did not create CP42.

## Direct hardware identities
Service evidence establishes VG-8/VG-8EX with two `RA03-002 / TC170C110AF-002` CSP-2 devices, JV-2080 with one exact `TC170C110AF-002`, VG-8 IC23 as `TMP320P16PGL`, and IC22 as `TC140G12AF-0061`.

## CSP-2 state
Substantial host-side PRAM/CRAM/config/readback behavior and exact factory BowedPad program/preload state are recovered. Open: revision-specific physical semantics for several delayed-publication/control cases, exact IC22 reduction/routing, and E6 physical confirmation.

## IC23 state
The host-visible packet and much of the CPU-side controller state machine are recovered. Current bounded packet interpretation: word `0x28` low byte = physical string index; `0x2A` = amplitude/envelope field with packet-reject behavior; `0x2C` = pitch-period/state with invalid-pitch handling.

The ordinary active-note CPU controller path contains no calls to the recovered CSP PRAM/CRAM programming API, favoring a continuous hardware-side control architecture rather than per-note CPU DSP rewrites.

Open: literal `TMP320P16PGL` internal mask ROM; exact IC23/IC22 sideband scalar/encoding; exact historical internal controller implementation.

The IC23 behavioral controller is useful for clone research but is **not** represented as a literal emulator of the TMP320P16PGL ROM.
