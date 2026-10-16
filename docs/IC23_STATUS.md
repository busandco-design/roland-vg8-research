# IC23 / TMP320P16PGL Status

Service evidence identifies IC23 as `TMP320P16PGL`. Host packet handling must be scoped by firmware version; the original wording generalized EX analysis to all VG hosts.

## Version-scoped software evidence — 2026-10-16

Independent review of [issue #1](https://github.com/busandco-design/roland-vg8-research/issues/1) reproduced both reported assembled-image SHA-256 identities. See [the review](ISSUE_1_REVIEW.md) and [machine-readable results](../evidence/ISSUE_1_IC23_REPRODUCTION.json).

| Image | Verified E3 result | Limit |
|---|---|---|
| VG-8 1.04, issue hash `396230b8…ead4866` | Two exact `MOV AX,1000h; MOV ES,AX` signatures; six-word writer at linear `0x99534`; bytewise drain at `0x99571` | No EX-style word-read sequence found. This is not exhaustive proof that no other consumer or address alias exists. |
| VG-8EX 1.01, issue hash `c7045aaa…617c12` | Three signatures, including a word-consuming handler at file `0x1FF83` / linear `0x9FF83` | Software data flow; physical producer, bus decode, and timing remain unmeasured. |

These sites select `ES=0x1000`, giving CPU addresses `0x10028`, `0x1002A`, and `0x1002C`. Identifying that address window with a particular physical IC23/IC22 port remains an architectural interpretation pending board/bus confirmation.

In the EX handler, `0x28` low byte selects a string; values >=6 are rejected. Word `0x2A` bit **15** rejects the packet. Word `0x2C` bit **15** substitutes `0xFFFF` while retaining the packet. Other accepted pitch/state values are stored alongside the scaled envelope. The high byte of `0x28` is masked off in this handler. A separate RAM disable flag also gates acceptance.

The six state pointers are `0x433C, 0x437C, 0x43BC, 0x43FC, 0x443C, 0x447C`; they must not be confused with the adjacent envelope curve. The comparison against RAM `0x1150` controls an ES-register sequence, not packet rejection. Synthetic execution of the ordinary handler body passed 322 cases; NEC interrupt entry/exit and peripheral side effects were excluded.

Previously recovered downstream pitch smoothing, stability, note, envelope, attack, transition, and bend state describes the audited **EX** CPU controller path. It is not evidence that the same consumer runs in 1.04, nor a recovered IC23 ROM implementation.

The Roland patent sources added to [the source ledger](../evidence/TMP320P16_PUBLIC_SOURCE_LEDGER.csv) support a candidate behavioral detector. Custom-part equivalence remains unproven.

## Literal ROM status
No verified non-invasive dump path has been recovered. The board configuration/family characteristics are consistent with internal mask-ROM execution. No public updater payload or service command currently provides the internal program.

**Behavioral controller reference:** available for research.

**Literal cycle-accurate TMP320P16PGL emulator:** not available.
