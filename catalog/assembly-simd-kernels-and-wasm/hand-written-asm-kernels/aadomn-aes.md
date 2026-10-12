# aadomn/aes (fixsliced constant-time AES in Cortex-M and RV32I assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `ARM Cortex-M and RISC-V RV32I assembly, with C reference (opt32)` · `MIT` · 🟡 stale

> Fixsliced and barrel-shiftrows constant-time AES-128/256 in Cortex-M and RV32I assembly; claims bitsliced AES speed records on 32-bit microcontrollers.

| | |
|---|---|
| **Beats** | previous bitsliced and constant-time AES implementations on Cortex-M and RISC-V cited by the TCHES 2021 paper (not shown on the repo page); the repo's own portable C opt32 versions |
| **Claimed result** | Paper title: 'New bitsliced AES speed records on ARM Cortex-M and RISC-V'. README table (cycles per byte): AES-128 fully-fixsliced 84.3 on Cortex-M3 and 89.3 on E31, semi-fixsliced 87.1 / 93.4, barrel-shiftrows 94.8 / 78.9; AES-256 fully-fixsliced 115.6 / 122.4; masked AES-128 199.3 (semi) and 195.8 (fully) on Cortex-M4. No baseline row on the page. |
| **Workload** | constant-time AES-128 and AES-256 encryption in cycles per byte on a Cortex-M3 and a SiFive E31 RISC-V core, fixsliced (2 blocks in parallel) and barrel-shiftrows (8 blocks) representations; first-order masked AES-128 on Cortex-M4 |
| **Metric** | throughput |
| **Hardware** | ARM Cortex-M3, SiFive E31 RISC-V core, Cortex-M4 (masked version) |
| **Adoption** | 72 stars |
| **Last commit** | 2024-10-17 |
| **Links** | [repository](https://github.com/aadomn/aes) · [benchmark](https://github.com/aadomn/aes) |

## Verdict

Only the authors' own cycle counts are in the repo: non-unrolled AES-128 at 84.3 (fully-fixsliced), 87.1 (semi) and 94.8 (barrel-shiftrows) cycles per byte on a Cortex-M3 and 89.3, 93.4 and 78.9 on a SiFive E31, with precomputed round keys; no baseline row, compiler, flags or harness. The TCHES paper's abstract (search snippet only) reports 80 and 91 cpb for unrolled code and 21% and 26% gains over earlier bitsliced AES records, which are hand-written assembly rather than a compiler or stdlib baseline.

## Use it when

- Constant-time AES-128/256 encryption on Cortex-M3/M4 or RV32I cores without AES hardware, where table-based AES would leak through timing or cache
- CTR, GCM or CCM style modes that need only the forward cipher and can batch two blocks (fixsliced) or eight blocks (barrel-shiftrows) per call
- RAM-constrained parts: fixsliced round keys take 352 bytes (AES-128) or 480 bytes (AES-256), a quarter of barrel-shiftrows' 1408/1920 bytes
- Bulk encryption on RV32I (E31-class) cores, where barrel-shiftrows is fastest in the README table (78.9 cpb for AES-128)
- As a reference for porting fixsliced AES; RustCrypto's aes crate soft backend is adapted from this repo's C code

## Skip it when

- Decryption (ECB/CBC decrypt, AES key unwrap): no inverse cipher in any directory; RustCrypto's port added one if you need it
- Single-block or latency-bound use: every call costs two blocks (fixsliced) or eight (barrel-shiftrows), so one-block calls roughly halve or eighth the effective throughput
- Cores with AES instructions (Armv8-M with crypto, Armv8-A, Zkne RISC-V): hardware AES is far faster; this code targets 32-bit cores without it
- When you need a tested, maintained library with KATs, modes and a build system: the repo has no test vectors, no harness and no build files, and the last code change is from 2022
- Side-channel-hardened deployments relying on the masked variant: the README itself warns no practical security evaluation was done and the RNG code is hard-wired to the STM32F407VG

## How it is fast

Bitslicing packs two blocks into eight 32-bit words so the S-box becomes a fixed Boolean circuit (the S-box code is credited to Ko-/aes-armcortexm in the source) with no table lookups. Fixslicing then never performs ShiftRows explicitly: it lets the state drift through four alternative representations and folds the correction into four specialised MixColumns routines (mixcolumns_0..3), resynchronising once at the end with double_shiftrows; the paper reports 52% fewer linear-layer operations than the previous fastest 32-bit bitsliced AES. The semi-fixsliced variant uses fewer MixColumns variants for smaller code; barrel-shiftrows reorders 8 blocks so ShiftRows becomes register renaming, which wins on register-rich RV32I.

## Compared with alternatives

Pick it over AVR-AES-faster when the target is a 32-bit Cortex-M or RV32I core rather than 8-bit AVR and constant time matters, and over libgcrypt or Nettle assembly when the core has no AES instructions and you want a small, freestanding, table-free source drop rather than a full library.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (masked variant needs the STM32F407VG hardware RNG at 0x50060804/0x50060808) |
| **Minimum toolchain** | GNU as with .syntax unified Thumb-2 for Cortex-M; RV32I GNU toolchain for riscv/\*.S; opt32 C needs GCC or Clang (SWAPMOVE uses a GNU statement expression) |
| **Platforms** | ARM Cortex-M3/M4 (Thumb-2, Armv7-M), RV32I (benchmarked on SiFive E31), any 32-bit or 64-bit target via the opt32 C code |
| **Thread safety** | Reentrant: functions keep state on the stack and in caller-supplied buffers (not documented, from reading the assembly) |
| **Drop-in for the baseline** | partial — encryption-only two-block (or eight-block) raw-block API with separate key schedule; no mbedTLS/OpenSSL-style interface, modes or decryption |

## Gotchas

- Bug found this session: in armcortexm/fixslicing/aes_keyschedule.s all four bitsliced key schedules (aes128/aes256 _ffs/_sfs) load the first key twice (ldr from [r1] for both halves) and never read key1, although aes.h declares key0/key1 and the comments say two different keys are supported; the RISC-V and opt32 versions read both keys. Issue #3 reported the same 'first input key was loaded twice' bug in the masked key schedule in Nov 2022 and only that file was fixed. Passing two distinct keys on Cortex-M silently encrypts block 1 under key0. Single-key use (key0 == key1) and the published cycle counts are unaffected.
- The \*_lut key schedules (the only key schedule for barrel-shiftrows on every ISA) index an S-box table with key bytes, so key expansion is not constant-time on cores with data caches or timing-variable memory; only the bitsliced fixsliced key schedules are table-free.
- API differs per ISA: barrel-shiftrows takes (ctext, rkeys, ptext) on ARM but (out, in, rkeys) on RISC-V and (ctext, ptext, rkeys) in opt32; the riscv and opt32 fixsliced aes.h declare AES-256 key arguments as [16] instead of [32] (harmless in C, misleading).
- RV32I code reads plaintext and keys with lw, so buffers should be 4-byte aligned (misaligned lw traps or is emulated slowly on E31-class cores); the Cortex-M encryption code was changed to plain ldr for unaligned inputs in PR #1 (Dec 2020).

## Known shortcomings

- No baseline or harness in the repo; the TCHES 2021 paper (21%/26% over prior records) is blocked here and known from snippets only, paper-access retier candidate for B. Last commit 2024-10-17.
- Enricher: all four Cortex-M bitsliced key schedules in armcortexm/fixslicing/aes_keyschedule.s (aes128/aes256 _ffs/_sfs) load key0 twice and never read key1 although aes.h declares two keys (issue #3 reported the same bug for the masked file only, fixed November 2022; RISC-V and opt32 read both keys), so two distinct keys on Cortex-M silently encrypt block 1 under key0; the published cycles per byte use one key with precomputed round keys and are unaffected; encryption only; the \*_lut key schedules index a table with key bytes (not constant-time); argument order differs per ISA; RustCrypto's aes soft backend is adapted from this repo's C code. Lead: Ko-/aes-armcortexm.

## Caveats and trade-offs

Repo page gives only the authors' own cycle counts for non-unrolled code (the README says unrolling is slightly faster and refers to the paper); no baseline row, compiler, flags or benchmark harness in the repo. The comparison to earlier work is in the peer-reviewed TCHES 2021 issue 1 paper (pp. 402-425, ePrint 2020/1123, IACR artifact tches/2021/a6), which could not be opened here. Search snippets only: the TCHES abstract reports fixsliced AES-128 at 80 and 91 cycles per byte on ARM Cortex-M and E31 RISC-V with precomputed round keys, improving the previous records by 21% and 26% (the ePrint version says 80 and 87 cpb, 21% and 30%), and the CHES 2021 slides cite prior bitsliced AES-128 at 102 and 125 cpb. The baseline is earlier hand-written bitsliced AES, not compiler -O3 output or a stdlib, so it is off the category baseline. The C opt32 directory is didactic and not benchmarked. The masked implementation has no practical security evaluation (README caution) and its RNG code is specific to the STM32F407VG board.

Fixsliced variants need only 352 bytes (AES-128) of round keys for 2 blocks in parallel; barrel-shiftrows needs 1408 bytes and 8 blocks; fully-fixsliced is faster but has larger code size; constant-time with no table lookups; separate assembly per ISA, aimed at 32-bit microcontrollers.

## Maintenance

Stale (last commit 2024-10-17 README only, last code fix 2022-11-30, issue #2 closed 2026-05-30 without code change); MIT, 72 stars, small enough to vendor, but the unfixed Cortex-M two-key bug and missing tests mean you should add your own known-answer tests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo README gives only the authors' own cycles-per-byte figures (all match the record) with no baseline row, no compiler, flags or board details, and the repo contains no benchmark harness (armcortexm/fixslicing holds only aes.h and .s files). The peer-reviewed TCHES 2021 comparison could not be opened (eprint.iacr.org, tches.iacr.org, artifacts.iacr.org and the rub.de mirror all fail DNS here), so the B lift stays pending.
- **Verifier notes:** Numbers match the README; tier stays C and is a candidate for a paper-access retier to B once the TCHES paper or the IACR artifact page is reachable (abstract claims 21% and 26% over previous records, snippet only). Last commit 2024-10-17 (README update), so stale; 72 stars, MIT. Shortcomings: no baseline or methodology in the repo, off-category baseline (prior hand-written bitsliced AES).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-69 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/aadomn/aes>
  - <https://github.com/aadomn/aes/commits>
  - <https://github.com/aadomn/aes/tree/master/armcortexm/fixslicing>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/aadomn/aes>
  - <https://github.com/aadomn/aes/commits>
  - <https://github.com/aadomn/aes/tree/master/armcortexm/fixslicing>
  - <https://github.com/aadomn/aes/tree/master/riscv/fixslicing>
  - <https://github.com/aadomn/aes/tree/master/opt32/fixslicing>
  - <https://github.com/aadomn/aes/issues?q=is%3Aissue>
  - <https://github.com/aadomn/aes/issues/2>
  - <https://github.com/aadomn/aes/issues/3>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/README.md>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/armcortexm/fixslicing/aes.h>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/armcortexm/fixslicing/aes_encrypt.s>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/armcortexm/fixslicing/aes_keyschedule.s>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/armcortexm/fixslicing/aes_keyschedule_lut.s>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/armcortexm/barrel_shiftrows/aes.h>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/armcortexm/1storder_masking/aes.h>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/armcortexm/1storder_masking/aes_keyschedule.s>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/riscv/fixslicing/aes.h>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/riscv/fixslicing/aes_keyschedule.S>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/riscv/fixslicing/aes_encrypt.S>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/riscv/barrel_shiftrows/aes.h>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/opt32/fixslicing/aes.h>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/opt32/fixslicing/aes_encrypt.c>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/opt32/fixslicing/aes_keyschedule.c>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/opt32/fixslicing/internal-aes.h>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/opt32/fixslicing/aes_keyschedule_lut.c>
  - <https://raw.githubusercontent.com/aadomn/aes/HEAD/opt32/barrel_shiftrows/aes.h>
  - <https://github.com/RustCrypto/block-ciphers/tree/master/aes/src>
  - <https://raw.githubusercontent.com/RustCrypto/block-ciphers/master/aes/src/backends/soft.rs>
  - <https://raw.githubusercontent.com/RustCrypto/block-ciphers/master/aes/src/backends/fixslice/mod.rs>
  - WebSearch: "Fixslicing AES-like Ciphers" Cortex-M3 cycles per byte previous record (snippets of tches.iacr.org/index.php/TCHES/article/view/8739)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/aadomn/aes`) · [data/wave13/enrich/raw/github_com_aadomn_aes.json](../../../data/wave13/enrich/raw/github_com_aadomn_aes.json) (enrichment confidence 0.75)

</details>
