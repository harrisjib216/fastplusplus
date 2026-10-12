# Bitsliced AEGIS-128L / AEGIS-128X2 (constant-time, no-AES-NI platforms)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Constant-time bitsliced C AEGIS for CPUs without AES instructions; beats bitsliced AES-GCM by 1.4-6x.

| | |
|---|---|
| **Beats** | OpenSSL AES-GCM / BoringSSL AES-GCM (side-channel-protected/bitsliced builds) |
| **Claimed result** | Paper Table 2, 16 KB messages, vs side-channel-protected (bitsliced) AES-128-GCM: ARM Cortex-A53 423 Mb/s (AEGIS-128L) vs 261 Mb/s (OpenSSL 3.3), 1.6x; SpacemiT X60 RISC-V 193 (128L) / 333 (128X2) vs 137 Mb/s (BoringSSL), 1.4-2.4x; SiFive U74 182 / 311 vs 130 Mb/s, 1.4-2.4x; WebAssembly on an Apple M1 host 2241 / 2912 vs 480 Mb/s, 4.7-6.1x. Cortex-M4: 185 cycles/byte (bitsliced AEGIS-128L) vs 246 (fixsliced AES-128-GCM, protected GHASH) and 208 (unprotected table AES-128-GCM). Table 3, pure TypeScript on Apple M5 Max/Bun, 1 MB: 324 MB/s (AEGIS-128L) vs 182 MB/s (noble AES-128-GCM, 1.8x) and 256 MB/s (noble ChaCha20-Poly1305, 1.3x). |
| **Workload** | Single-core, 16 KB message AEAD encrypt+authenticate throughput on ARM/RISC-V CPUs lacking AES instructions and on WebAssembly, plus ARM Cortex-M4 cycle counts, vs side-channel-protected (bitsliced) AES-128-GCM from OpenSSL 3.3 (on Cortex-A53) and BoringSSL (elsewhere); also a pure-TypeScript benchmark on Apple M5 Max/Bun vs the noble-ciphers pure-JS AES-GCM and ChaCha20-Poly1305. |
| **Metric** | throughput |
| **Hardware** | ARM Cortex-A53 (64-bit); SpacemiT X60 (RISC-V, no AES ext.); SiFive U74 (RISC-V, no AES ext.); WebAssembly on an Apple M1 host; ARM Cortex-M4 microcontroller; Apple M5 Max (pure TypeScript under Bun) |
| **Adoption** | 9 stars (aegis-aead/aegis-bitsliced); companion pure-TypeScript port jedisct1/js-aegis-aead (MIT, 4 stars) used for the JS numbers |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/aegis-aead/aegis-bitsliced) · [benchmark](https://eprint.iacr.org/2026/1338.pdf) |

## Verdict

In the author's own preprint (ePrint 2026/1338), measured on 16 KB messages, one core, wall-clock time with the tag included, against bitsliced AES-128-GCM (OpenSSL 3.3 on Cortex-A53, BoringSSL elsewhere): A53 423 vs 261 Mb/s; X60 193 (128L) / 333 (128X2) vs 137; U74 182 / 311 vs 130; WASM on M1 2241 / 2912 vs 480; Cortex-M4 185 vs 246 cycles/byte. Compilers and flags are not stated, and the repo's benchmark.zig times only AEGIS, not the AES-GCM baselines.

## Use it when

- Timing-safe AEAD on ARM Cortex-A53-class or RISC-V cores without AES extensions (SiFive U74, SpacemiT X60), where the alternative is bitsliced OpenSSL/BoringSSL AES-128-GCM: 1.6x (A53) and 1.4-2.4x (RISC-V, X2 at the high end) on 16 KB messages.
- WebAssembly builds with simd128 that must stay constant-time: the paper reports 2241-2912 Mb/s vs 480 Mb/s for bitsliced BoringSSL AES-GCM on an Apple M1 host.
- Microcontrollers without an AES peripheral (Cortex-M4): 185 cycles/byte vs 246 for fixsliced AES-128-GCM with protected GHASH.
- Mixed fleets already standardized on AEGIS, where some endpoints (IoT, WASM clients) lack AES hardware and others use libaegis or libsodium. Ciphertexts are the same RFC 10032 format.
- Pure JS/TS via the companion js-aegis-aead port: 324 MB/s at 1 MB on Apple M5 Max/Bun, 1.8x noble AES-128-GCM and 1.3x noble ChaCha20-Poly1305.

## Skip it when

- Any CPU with AES-NI, ARMv8 Crypto or VAES. Use libaegis, whose README reports 100+ Gb/s for hardware-accelerated AEGIS-128L on Zen 4 and Apple M1. If you do not need side-channel protection, libaegis's unprotected table-based AEGIS-128L is also 1.85x (A53, 782 Mb/s) to 2.8x (U74, 507 Mb/s) faster than this code.
- Microcontrollers with an AES accelerator: on the Flipper Zero Cortex-M4, hardware AES-GCM does 46 cycles/byte vs 185 here.
- Workloads that need streaming or incremental encrypt/decrypt, AEGIS-MAC, a raw keystream, or the X4 variants. Only one-shot whole-buffer calls for 128L/128X2/256/256X2 exist.
- Where the margin is thin: on SpacemiT X60, bitsliced AEGIS-128L (193 Mb/s) is slower than unprotected OpenSSL AES-GCM (223). On Cortex-M4 it is only about 3% ahead of fixsliced AES-GCM with a 4-bit-LUT GHASH (185 vs 190 cycles/byte). Very short messages are dominated by fixed init/finalization cost.
- Risk-averse deployments: single-author code with 9 stars, no tagged releases and no issue history, backed only by a non-peer-reviewed preprint from the author.

## How it is fast

An AEGIS-128L update applies one keyless AES round to all 8 state blocks at once, so a single message stream fills an 8-block bitsliced datapath. Bitsliced AES-CTR needs 8 independent counter blocks for that, and the paper reports AEGIS-128L needs 2.5x fewer parallel AES rounds per byte than bitsliced AES-128-CTR, with no GHASH multiply. The code uses Adomnicai and Peyrin's barrel-shiftrows representation with the Maximov-Ekdahl S-box circuit. It keeps the state bitsliced across init, AD, message and finalization, and computes the keystream directly in packed lanes with only a partial unpack. AEGIS-128X2 uses 64-bit words to update 16 blocks per round on 64-bit and WASM targets. With clang or GCC 12+, the S-box runs as 4x32-bit vectors on SSE2, NEON, AltiVec or WASM SIMD128.

## Compared with alternatives

Pick this over libaegis only when the target has no AES instructions and timing side channels matter; libaegis's own README recommends aegis-bitsliced for such environments. The HiAE, Rocca and intel-ipsec-mb figures in the catalog were all measured on hardware-AES x86 CPUs, so none of them addresses AES-less, constant-time targets.

## Integration

| | |
|---|---|
| **Form** | static lib (zig build) or source-drop (7 plain C files plus headers in src/) |
| **Dependencies** | none beyond libc (string.h/stdlib.h) |
| **Minimum toolchain** | Zig build system; build.zig uses the b.addLibrary/root_module API, but no minimum Zig version is declared and there is no CMake. The vectorized S-box needs clang or GCC 12+, otherwise the scalar path is used. The C standard is not documented. |
| **Platforms** | Portable C on 32- and 64-bit targets. The 64-bit doubled X2 layout is auto-selected on 64-bit and wasm, and 32-bit targets use two interleaved 32-bit states. The vector S-box covers SSE2, NEON, AltiVec and WASM simd128. Measured on Cortex-A53, Cortex-M4, SiFive U74, SpacemiT X60 and WASM. |
| **Thread safety** | Not documented. There is no init call and no mutable global state (only a never-written volatile optimization blocker in tag comparison), so the one-shot functions look reentrant on inspection. |
| **Drop-in for the baseline** | no |

## Gotchas

- Exports the same public symbols as libaegis (aegis128l_encrypt, aegis_verify_16, ...), so both cannot be linked into one binary without renaming.
- On WebAssembly the vector path needs the simd128 target feature (e.g. -Dcpu=lime1+simd128). Without it, the README says the code runs 2-3.3x slower under wasmtime.
- README WASM numbers (AEGIS-128L 3429, X2 3154 Mb/s) differ from the paper (2241 / 2912), including which variant wins. Benchmark your own target and build.
- No incremental API, so whole messages must be in memory. On tag failure, decrypt zeroes the plaintext buffer and returns -1.

## Known shortcomings

- ePrint preprint by the repo's author, not peer-reviewed; bench.zig times AEGIS only, no flags stated. The 333 figure on the X60 is AEGIS-128X2, not 128L; README WASM numbers differ from the paper.
- Thin or negative margins: on the X60, AEGIS-128L (193 Mb/s) is slower than unprotected OpenSSL AES-GCM (223); on Cortex-M4 185 vs 190 cycles/byte against fixsliced AES-GCM, while hardware AES-GCM on M4 runs at 46. Baselines are not in the repo harness; compilers/flags unstated. One-shot API only (no incremental, MAC or X4); exports the same symbol names as libaegis, so both cannot be linked together. 9 stars, no releases.

## Caveats and trade-offs

Published 2026-06/07 as a non-peer-reviewed preprint by the implementation's author; not yet independently reproduced. The C/Zig benchmark harness (src/test/benchmark.zig) measures only AEGIS variants; the baseline AES-GCM runs are not part of the published code, and compilers/flags are unstated. The repo README currently shows different, higher WebAssembly figures (AEGIS-128X2 3154, AEGIS-128L 3429 Mb/s) than the paper (2912 / 2241 Mb/s). The JS comparison uses the companion repo jedisct1/js-aegis-aead, whose 'bun run bench' does include noble-ciphers, but that baseline is not the listed OpenSSL/BoringSSL one.

Purpose-built for platforms lacking AES/vector-AES instructions (microcontrollers, RISC-V without crypto extensions, WASM, plain JS). On hardware with AES-NI/VAES, hardware-accelerated AEGIS or the AEGIS-X modes (see separate entry) are faster than this bitsliced code.

## Maintenance

Actively maintained (last commit 2026-09-21, at least 100 commits since 2024-10) but untagged and lightly used. The LICENSE file is plain MIT (based on Adomnicai's MIT code) even though GitHub reports NOASSERTION, and the code is small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** ePrint 2026/1338 ('Bitslicing the AEGIS', Frank Denis) is a preprint by the repo author, not a peer-reviewed paper, so the evidence is first-party and B does not apply. It is not A either: the public harness (src/test/benchmark.zig) times only AEGIS, not the OpenSSL/BoringSSL AES-GCM baselines, and compiler/flags are unstated.
- **Verifier notes:** All claimed numbers appear in the paper, but the X60 figure (333 Mb/s) is AEGIS-128X2, not 128L, so I labeled the variants. GitHub reports license NOASSERTION; the LICENSE file is plain MIT (Frank Denis, based on Adomnicai's work). Repo: 9 stars, not a fork, last commit 2026-09-21 (active). ePrint lists the paper as CC0, but the code is MIT.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2026/1338.pdf>
  - <https://eprint.iacr.org/2026/1338>
  - <https://github.com/aegis-aead/aegis-bitsliced>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/LICENSE>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/README.md>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/build.zig>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/test/benchmark.zig>
  - <https://github.com/jedisct1/js-aegis-aead>
  - <https://github.com/jedisct1/js-aegis-aead/blob/main/README.md>
  - <https://api.crossref.org/works?query.bibliographic=Bitslicing+the+AEGIS+Denis&rows=3>
- **Sources the enricher read:**
  - <https://github.com/aegis-aead/aegis-bitsliced>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/README.md>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/LICENSE>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/build.zig>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/include/aegis.h>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/include/aegis128l.h>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/common.h>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/common.c>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/aes-bs8.h>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/aegis128l.c>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/aegis128x2.c>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/aegis128x2_64.c>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/test/benchmark.zig>
  - <https://github.com/aegis-aead/aegis-bitsliced/blob/master/src/test/main.zig>
  - <https://github.com/aegis-aead/aegis-bitsliced/commits/master>
  - <https://github.com/aegis-aead/aegis-bitsliced/issues>
  - <https://github.com/aegis-aead/aegis-bitsliced/pulls>
  - <https://github.com/aegis-aead/aegis-bitsliced/releases>
  - <https://eprint.iacr.org/2026/1338.pdf>
  - <https://eprint.iacr.org/2026/1338>
  - <https://github.com/jedisct1/js-aegis-aead>
  - <https://github.com/jedisct1/js-aegis-aead/blob/main/README.md>
  - <https://github.com/aegis-aead/libaegis/blob/main/README.md>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/common/softaes.c>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/aegis-aead/aegis-bitsliced`) · [data/wave7/enrich/raw/github_com_aegis_aead_aegis_bitsliced.json](../../../data/wave7/enrich/raw/github_com_aegis_aead_aegis_bitsliced.json) (enrichment confidence 0.82)

</details>
