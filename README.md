# Roland VG-8 / VG-8EX BowedPad Open Reverse-Engineering Project

This repository seed is for an **open, evidence-driven preservation and emulation effort** focused on the Roland VG-8 / VG-8EX factory BowedPad / V-BOW processing path.

## Goal

The primary engineering goal is an observable/output-equivalent software implementation of the factory BowedPad behavior, while keeping a strict distinction between direct VG-8/VG-8EX evidence, same-chip comparative evidence, broader CSP/ESP-family evidence, reproducible software inference, behavioral substitutes, and physical hardware observations.

A complete motherboard-level VG-8 emulator is a broader goal and may require additional evidence, especially the unavailable internal program ROM of the `TMP320P16PGL` pitch/envelope DSP.

## Current authority

`CP41_AUTHORITATIVE_E3_FACTORY_CORE_AND_EXACT_PRELOAD_TRANSACTION_EQUIVALENCE`

Post-CP41 research may narrow open questions, but it does not become silicon truth merely because it is plausible or executable.

## Non-negotiable evidence boundary

`E6` — genuine physical CSP-2 observation — is still absent.

No claim of CSP-2 silicon equivalence, literal TMP320P16PGL ROM equivalence, exact IC22 internal logic, or final 1:1 audible completion is made without qualifying evidence.

## What is intentionally NOT distributed here

This project is **not a firmware or ROM mirror**. Do not commit proprietary Roland/BOSS firmware or ROM images, copyrighted service-manual scans, unpublished third-party research without permission, private correspondence, credentials, personal data, or access-controlled material.

Where useful, the project records hashes, provenance, offsets, extraction procedures, and analysis scripts so users can work from lawfully obtained source files.

## AI-assisted research disclosure

AI has been used extensively for document/code triage, static-analysis assistance, hypothesis generation, script drafting, reconciliation, test design, and documentation. AI output is **not evidence by itself**. Every admitted technical claim must retain a source/evidence class and, where applicable, reproducible verification.

See `AI_DISCLOSURE.md`, `EVIDENCE_POLICY.md`, and `PUBLICATION_POLICY.md`.

## Collaboration

Contributions are welcome when they preserve provenance, distinguish evidence from inference, respect rights/permissions, include reproducible methods where possible, and avoid overstating hardware behavior.

The project is independent and is not affiliated with or endorsed by Roland Corporation, BOSS, Toshiba, Texas Instruments, The Usual Suspects, or any individual researcher.

## Licensing

Original project **software/code** is licensed under **GPL-3.0-or-later** unless a file states otherwise.

Original project **documentation** is licensed under **CC BY-SA 4.0** unless a file states otherwise. See `LICENSE-DOCS.md`.

Third-party material remains under its original copyright/license terms and must not be relicensed merely because it is referenced here.
