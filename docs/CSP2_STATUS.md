# CSP-2 Status

Exact-chip products currently admitted: VG-8 / VG-8EX (2 × `TC170C110AF-002`) and JV-2080 (1 × `TC170C110AF-002`). No third exact-chip product is presently admitted.

The VG firmware exposes PRAM/CRAM programming, host configuration, read-trigger/result-window behavior, JIG memory tests, and exact factory BowedPad/D62 program/preload state. JV-2080 v1.02 supplies valuable same-chip host-software comparison.

Comparative CSP/ESP research strongly constrains several architectural behaviors, but exact VG CSP-2 physical confirmation remains required for unresolved revision-specific claims. The active physical gate therefore remains open.

## Issue #1 review — 2026-10-16

ALX9797 [reports](https://github.com/busandco-design/roland-vg8-research/issues/1) improved factory-program behavior with IRAM operand offsets halved before ring-position addition, and no behavioral distinction among five serial-input-store candidates in their harness. These are reported software results, not confirmed CSP-2 addressing or serial-port semantics.

The retained CP41 core uses an unshifted effective IRAM offset after a full instruction-byte-order correction. Its E3 status is not a hardware oracle against which the contributor's interpretation can be rejected. Conversely, greater output energy or plausible pitch following does not establish correct addressing. Decoder units, initialization, coefficient timing, ring stride, and serial latching must be matched first.

An independent 512-frame screen using the plain retained core, authentic D62 static preload arrays, zero runtime memory, and synthetic inputs produced zero output under both shifts. This screen omitted the full admitted execution path and live updates, so it is **inconclusive**, not a replication or refutation of the reported PAD/Pipe results. See [configuration and results](../evidence/ISSUE_1_CSP_SCREEN.json).

CP41's qualified factory-selection/preload-transaction authority is retained. No DSP semantic change or new checkpoint is admitted. The [review](ISSUE_1_REVIEW.md) specifies the missing reproduction bundle and a discriminating next experiment. No E6 evidence was obtained.
