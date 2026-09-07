# TMS320C1x TBLR Self-Read Proof Model

## Result

`PASS_DOCUMENTED_C1X_TBLR_TO_DATA_RAM_TO_OUT_SYNTHETIC_PROOF__CUSTOM_TMP320_VALIDATION_OPEN`

A minimal independent Python model was written from public first-generation TMS320 instruction semantics.

Synthetic 8K-word program memory was populated with known sentinel words at addresses `0x0000`, `0x0123`, and `0x1FFF`. For each sentinel the model performed:

```text
ACCL = program address
TBLR -> data RAM
OUT  -> I/O port
```

All sentinels were recovered exactly.

## What this proves

It proves only that the documented standard C1x instruction semantics are internally sufficient to implement a software ROM-export loop if controlled code is executing while the target ROM is mapped.

This agrees with the current MAME TMS320C1x implementation, where `tblr()` reads program memory at the low accumulator address and writes the result into data memory.

## What this does not prove

- that `TMP320P16PGL` is instruction-for-instruction identical to stock C16;
- that VG-8 exposes a way to execute arbitrary IC23 code;
- that MC/MP can be switched dynamically;
- that the VG board can be safely reconfigured for external execution;
- that any internal ROM byte has been recovered.

No hardware action was performed.
