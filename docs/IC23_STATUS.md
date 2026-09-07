# IC23 / TMP320P16PGL Status

Known from service/firmware evidence: IC23 is the `TMP320P16PGL` custom pitch/envelope DSP. The VG host consumes a small interface window; the recovered packet handler reads aligned words at offsets `0x28`, `0x2A`, `0x2C`.

Recovered CPU-visible behavior: `0x28` low byte selects one of six strings; `0x2A` participates in envelope/amplitude processing and has packet-reject behavior; `0x2C` carries pitch-period/state and supports an invalid-pitch state.

Downstream CPU code reconstructs accepted/smoothed pitch, pitch error/stability, note coordinate, current/hold envelopes, envelope slope/trend, attack state, transition hold, note state, and bounded bend/pitch-motion state.

## Literal ROM status
No verified non-invasive dump path has been recovered. The board configuration/family characteristics are consistent with internal mask-ROM execution. No public updater payload or service command currently provides the internal program.

**Behavioral controller reference:** available for research.

**Literal cycle-accurate TMP320P16PGL emulator:** not available.
