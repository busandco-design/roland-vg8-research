# Technical review of issue #1 — 2026-10-16

Reviewed against public commit `262250b1e8677d747028d77b7730a8b94e01cfbc`, the retained CP41 package, locally held firmware/update artifacts, and primary patent documents. [ALX9797's issue](https://github.com/busandco-design/roland-vg8-research/issues/1) was open with zero comments when retrieved. No physical device was driven or measured. AI-assisted analysis is disclosed under the existing project policy.

## Disposition

| Finding | Review result | Effect on existing evidence |
|---|---|---|
| Different 1.04 / EX packet handling | Exact image hashes and signature counts reproduced; identified drain and EX consumer verified in software. Several details need correction. | Correct the public documentation's version scope. The exhaustive claim that 1.04 has no CPU consumer is not established. |
| Patent detector architecture | Both primary texts retrieved and the citation relationship verified. | Useful candidate algorithm sources; no recovered TMP320 program, packet units, or clock established. |
| Halved IRAM operands | Exact contributor experiment remains unreproduced. A different, explicitly bounded screen was inconclusive. | Retain as an E5 hardware hypothesis supported by contributor-reported E3 behavior. Do not change the admitted core. |
| Five serial-store candidates equivalent | Contributor-reported negative result with insufficient harness detail for independent rerun. | Preserve its tested-domain scope; it does not identify real serial timing or rule out all store semantics. |
| Fixed work slot and live updates | Reported transaction corroboration is compatible with CP41's bounded load evidence; exact trace correspondence is still required. | No new checkpoint, silicon equivalence, or audible-completion claim. |

## Firmware provenance and reproduction

The earlier retained comparison archive supplied ordinary decoded streams, not the issue's padded images. The MSI CP41 EX fixture independently had the same ordinary-stream hash. The following transforms reproduce the issue hashes exactly; padding is container reconstruction, not evidence that those bytes were programmed on a board.

| Image | Ordinary stream | Exact assembly transform | Assembled size |
|---|---|---|---|
| VG-8 1.04 | `0x5FC00` bytes | Prepend `0x400` zero bytes | `0x60000` bytes |
| VG-8EX 1.01 | `0x7FD00` bytes | Prepend `0x100` and append `0x200` zero bytes | `0x80000` bytes |

SHA-256 identities:

- 1.04 ordinary: `a91607c17bfe7454fadf6efb447f60b58e33b08b2f3f83eea3d892ae769c50b3`
- 1.04 assembled: `396230b85affbc975c6bd39182d44862cae39f64fab7d23dfd7951ae8ead4866`
- EX ordinary: `1cb26b616f407a38799c6038d4224652b85d20dfde7b42c33e93ae7b2c2cc287`
- EX assembled: `c7045aaa10f3eaa020e64e045c4ba7497c4c093801d4f3d1c9d8ccf2ce617c12`

The 1.04 stream was freshly reconstructed from the locally held `VG8V104.zip`: 3,064 ordinary DT1 packets, all passing Roland's 7-bit checksum, yielded 392,192 bytes identical to the retained stream. The EX ordinary stream was recovered from retained artifacts; its original updater was not reconstructed in this review. Neither firmware image is redistributed.

Run `tools/review_issue1_ic23.py` with locally supplied files:

```sh
python tools/review_issue1_ic23.py --v104 /path/to/v104.bin --ex /path/to/ex101.bin --updater /path/to/VG8V104.zip
```

The script accepts the known ordinary or assembled forms, rejects mismatched assembled hashes, and requires Capstone and Unicorn (plus Mido for updater reconstruction). The recorded run used Python 3.12.14, Capstone 5.0.7, Unicorn 2.1.4, and Mido 1.3.3. Results: [IC23 reproduction receipt](../evidence/ISSUE_1_IC23_REPRODUCTION.json).

## IC23: what is verified, corrected, and still inferred

The exact segment-load signature occurs at assembled file offsets `0x19534, 0x19571` in 1.04, and `0x1FE32, 0x1FE6F, 0x1FF83` in EX. In the retained EX ordinary stream the last site is `0x1FE83`; with its documented base `0x80100`, the linear address is `0x9FF83`. Thus the assembled EX layout is consistent with base `0x80000` for these sites. The segment load is inside the handler; the retained handler entry is `0x9FF7E`.

The 1.04 primitive reads six consecutive bytes through AL at `ES:0x28..0x2D`, without local packet parsing or a ring write. Successive reads overwrite AL, although its final value survives return. “Drain” describes this observed routine, not a demonstrated peripheral acknowledgement mechanism. EX adds a word-consuming sequence; its 18-byte read sequence has zero matches in the 1.04 image.

The physical address arithmetic is exact: `0x1000 << 4 = 0x10000`, then add the displacement. A particular chip's electrical decoding/ownership of that window is not proved by CPU instructions alone.

Corrections to the issue's EX interpretation and caller inventory:

| Item | Independently checked result |
|---|---|
| Invalid flags | `TEST AH,80h` and `TEST DH,80h` test **word bit 15**, not word bit 7. Amplitude invalid rejects; pitch invalid stores `0xFFFF`. |
| RAM `0x1150` comparison | Both branch outcomes proceed to acceptance checks. Equality executes two ES loads; it does not act as a string-rejection filter. The purpose/side effects of those ES loads remain unresolved. |
| State pointers at `CS:0xAC` | `0x433C, 0x437C, 0x43BC, 0x43FC, 0x443C, 0x447C`. The values quoted as pointers in the issue belong to the adjacent nonlinear envelope table. |
| Envelope arithmetic | High word of unsigned amplitude × per-string scale enters the eight-segment mapping; high word >=`0x2000` saturates to `0x7FFF`. The threshold is not applied directly to the raw amplitude word. |
| “Only callers” of the 1.04 drain | Three direct far calls also occur at linear `0x993E6, 0x993EB, 0x993F0`, outside `0x9958F`; the last is followed by an AX overwrite. The three near calls within `0x9958F` are not the complete caller inventory. |

322 synthetic handler-body executions covered string bounds/high-byte masking, enable/disable gating, both comparison outcomes, amplitude/pitch flags, scaling, saturation, and randomized valid values. These execute the ordinary x86 instructions with synthetic RAM and packet values and stop before the NEC-specific epilogue. They do not emulate the NEC interrupt mechanism, electrical ES side effects, or IC23.

The issue's scanner also skips the first post-signature byte: the signature is five bytes, but its preview begins at `i+6`. This does not change its match count; previews should start at `i+len(pattern)`.

Limits: an exact signature search cannot exclude other segment-load encodings, aliases, indirect calls, or semantically different consumers. A different revision would narrow revision scope rather than falsify facts tied to these exact hashes. The justified documentation correction is version-specific reporting, not “all original VG-8 firmware never uses pitch information.”

## Patent evidence

[JPH07110687A](https://patents.google.com/patent/JPH07110687A/en), particularly paragraphs 0009–0028, describes adaptive positive/negative peak detection, crossings of the detector difference signals, an SR latch, and sample counting with optional interpolation. Its text also permits single-polarity detection. The public Japanese text and machine translation were available; technical wording should be checked against the original where consequential.

[US20050145103A1](https://patents.google.com/patent/US20050145103A1/en) explicitly cites that publication. Figures 1–3 add pitch/envelope bus outputs and an interrupt connection. **32 kHz and K=0.99/0.01 are examples**, not VG-8 measurements. LPF coefficients, fixed-point details, and exact VG-8 interrupt cadence remain unspecified; F/INT alone does not prove one interrupt per half-period. This is a citation relationship, not proof of one patent family or one chip implementation.

Admit the documents as E2 manufacturer-authored evidence, the architectural comparison as E4, and any proposed TMP320 mapping as E5. Neither source identifies the custom mask-ROM program. New ledger entries preserve that distinction.

## CSP-2: no basis yet for a semantic promotion

The reported ~117M versus ~9.9M slot-17 “energy,” 220/330 Hz following, and pluck decay lack an exact core commit/diff, fixture hashes, stimulus, initialization, sample count/warm-up, output tap, metric definition, and coefficient-event stream. The cited `giulioz/roland-dsps` repository returned 404 during this review, so its current contents could not supply those missing inputs. A fork, archived commit, or minimal patch is needed.

The retained CP41 executor hash is `018673a5d8ed5e80dd145df82ad8feccad31d498e8178d670f2cb737876ef1f4`. It uses a full CSP-2 instruction-byte swap followed by `(ring_position + effective_offset) & 0x1FF`; it does not halve the effective offset. Raw instruction bits, decoded offsets, special-register selectors, and actual IRAM array indices must be compared separately. Shifting adjacent decoded offsets can alias two locations; shifting a special-register selector can instead change the operation altogether.

[The independent screen](../evidence/ISSUE_1_CSP_SCREEN.json) used authentic CP41 D62 preload hashes with the plain frozen base executor, full byte-order correction, zero runtime memory, fixed synthetic lane 0/control signals, 32 kHz, 512 frames per run, and synchronous CSP0-first execution. It changed only IRAM read/write index calculation. Silence, 220 Hz, 330 Hz, and a decaying 220 Hz stimulus yielded all-zero output in both modes. This is a **non-discriminating screen**, not a failed replication of ALX9797's experiment and not a rerun of the full admitted CP41 path. It cannot establish tracking or decay. No further tuning was used to manufacture a positive result.

Reproduce that limited screen with locally held CP41 assets:

```sh
python tools/review_issue1_csp_screen.py --cp41-root /path/to/VG8_BowedPad_CP41_2026-09-04
```

The five reported serial-store candidates constrain only the tested programs and observation horizon. Without special-access coverage and first-divergence traces, equality could reflect dead/unobserved writes, later overwrites, or equivalent paths in that domain. Timing/latching is a reasonable next hypothesis, not an established cause.

## Checkpoint impact and BowedPad relevance

CP41 establishes a qualified E3 native factory core and bounded post-assembly/preload transaction equivalence. It explicitly retains synthetic selection dispatch, three differing postload shadows, conditional serial-route sensitivity, and an open silicon gate. None of issue #1 establishes a contradiction to those bounded claims. Its IRAM hypothesis challenges unresolved execution semantics, not the identity of recovered preload bytes.

The packet layout and EX CPU arithmetic substantially corroborate earlier work. The **version distinction** repairs a real public-documentation overgeneralization. The patents add candidate-model provenance. The halving observation adds a useful reproduction target but no demonstrated advance to hardware equivalence or audible completion.

The fixed work-slot report (`0x7380`, loader argument `0x2C`) should be compared against CP41's exact call/write traces before being counted as independent transaction equivalence. “Live coefficient updates are needed in our harness” does not imply ordinary per-note CPU PRAM/CRAM rewrites: loading, parameter updates, steady note handling, and hardware-side control are distinct phases. Require call-site/time evidence before revising the existing no-programming-call result for the audited EX active-note region.

## Highest-information remaining experiment

**Immediate priority: one matched-state, first-divergence IRAM experiment shared between the two cores.** Obtain a minimal runnable contributor harness with exact revision/diff and lawful local extraction instructions; hash PRAM, CRAM, initial IRAM/ERAM, accumulator/history/latch state, configuration, input, and timestamped coefficient writes. Preserve ring stride, decoding, routing, and special-register selectors. Cross offset shift 0/1 with zero initialization and captured post-initialization state, replaying the identical live event stream in every cell.

Start with a positive input-path control, then trace the first difference in `(chip, frame, PC, decoded offset, ring position, effective IRAM address, read/write value, serial latch)`. Compare against silence, record saturation and complete slot output, and define energy as a specified sum of squares over a fixed window. Do not interpret energy before the positive control works. If correct initialization rescues shift 0, the original result is initialization-dependent; if shift 1 remains necessary, minimize the trace before attributing it to silicon.

**Decisive physical follow-up:** a controlled adjacent-address sentinel test, using ordinary operands such as `0x20/0x21` at one known ring position, with pipeline settling and a verified readback/output path. Shift 0 predicts distinct storage; shift 1 predicts aliasing. A physical result would discriminate the addressing rules far more directly than “sounds right.” This requires a separately reviewed, authorized hardware procedure and is not claimed executed. A passive host-address/port capture under known single-string stimuli would separately test IC23 window ownership and packet cadence; IC23-only measurements must not be mislabeled as physical CSP-2/E6 observations.

## Evidence and publication boundary

No source ROMs, service scans, private correspondence, or third-party core code are included. The new scripts and receipts retain methods, hashes, derived instruction descriptions, and limitations. The existing CP41 authority and E6 boundary remain unchanged.
