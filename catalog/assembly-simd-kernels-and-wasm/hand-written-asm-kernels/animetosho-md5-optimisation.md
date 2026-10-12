# md5-optimisation (animetosho)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (inline x86, ARM and ARM64 assembly headers)` · `Apache-2.0 OR MIT` · 🟢 active

> Inline-asm single-stream MD5 for x86/ARM/AArch64; beats OpenSSL's hand-tuned x86 assembly by 4-17%, 26% with AVX-512.

| | |
|---|---|
| **Beats** | OpenSSL v1.1.1h MD5 (itself hand-tuned x86 assembly), reading from `openssl speed md5` at 16 KB |
| **Claimed result** | README: 'beat OpenSSL's implementation by roughly 5% in the general case, and 23% for processors with AVX512 support'; the % table is relative to the repo's 'Standard' control, e.g. Skylake-X GOpt +5.35%, NoLEA-G +9.70%, AVX512 +23.11% (4.734, 4.546 and 4.051 cpb vs \~4.99 cpb). The chart's data table (images/bench.png) also prints OpenSSL's absolute bytes/cycle: Skylake-X OSSL 0.196 vs Standard 0.201, GOpt 0.211, NoLEA+G 0.220 (about +12% over OpenSSL, derived from page data); Haswell OSSL 0.200 vs NoLEA+G 0.220 (+10%, derived); Piledriver OSSL 0.180 vs GHOpt 0.210 (+17%, derived); Merom OSSL 0.184 vs GHOpt 0.194 (+5%, derived); Airmont OSSL 0.157 vs NoLEA+GH 0.170 (+8%, derived); K10 OSSL 0.204 vs NoLEA+G 0.217 (+6%, derived); Jaguar OSSL 0.199 vs Cache8+G 0.207 (+4%, derived); AVX512 on Skylake-X about +26% over OSSL (derived from 4.051 cpb vs 0.196 B/cycle). |
| **Workload** | Single-buffer MD5 of long inputs, bytes per cycle normalised across seven x86 microarchitectures at locked frequency; the repo's hand-written x86 assembly variants versus a 'Standard' control schedule that the author says roughly equals OpenSSL. |
| **Metric** | throughput |
| **Hardware** | Merom, Haswell, Skylake-X, Airmont, K10, Piledriver, Jaguar (named by microarchitecture only, locked frequency); AVX512 variant measured on Skylake-X only |
| **Compiler and flags** | Clang 11.0.0 x86-64; Makefile at the benchmark commit e42661105: -O3 -static -std=c++11 -fno-rtti -fno-exceptions -ggdb (plus -mavx512vl for the AVX512 build; current Makefile adds a -mbmi build); OpenSSL v1.1.1h built statically, fastest of 3 `openssl speed md5` runs at 16 KB |
| **Adoption** | 159 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/animetosho/md5-optimisation) · [benchmark](https://github.com/animetosho/md5-optimisation#benchmarks-single-buffer) |

## Verdict

Single-buffer MD5 of 16 KB inputs was measured on seven x86 microarchitectures at locked frequency (Merom, Haswell, Skylake-X, Airmont, K10, Piledriver, Jaguar; Clang 11.0.0 -O3 -static). The best scalar variant per CPU beat the author's standard schedule by 1-10% and OpenSSL 1.1.1h's `openssl speed md5` by about 4-17% (derived from the chart's data table). The AVX-512VL variant ran at 4.051 vs 4.99 cycles per byte on Skylake-X (+23% over Standard, about +26% over OpenSSL, derived).

## Use it when

- Single-stream MD5 over long buffers where a file format or protocol mandates MD5 (PAR2, Content-MD5 or ETag checks, legacy checksums) and you control the build: GOpt or GHOpt gain about 5% on most cores tested and never lose more than 1.24% (GHOpt on K10).
- Intel CPUs with AVX-512VL (Skylake-X and later Intel): the AVX512 variant reached 4.051 cycles per byte vs 4.99 for the standard schedule on Skylake-X (+23%, about +26% over OpenSSL 1.1.1h, derived from page data).
- Fleets of one known microarchitecture, where you can pick the best variant from the table (NoLEA+G gives +9.7% on Skylake-X and Haswell).
- As a reference when writing MD5 for another language or ISA: FreeBSD's libmd amd64 md5block.S by Robert Clausecker, linked from discussion #9 (Phabricator D45670), ships baseline, BMI1 ANDN and AVX-512 vpternlogd kernels using the same ideas.

## Skip it when

- Anything security-relevant: MD5 is cryptographically broken. Use SHA-256 or BLAKE3.
- Hashing many independent streams at once: multi-buffer SIMD (Intel isa-l_crypto md5_mb, minio/md5-simd) gives far higher aggregate throughput than any single-buffer schedule.
- AMD Zen4 with the AVX-512 variant (2-cycle vector rotate latency, per the README). On Merom, Piledriver and Jaguar the NoLEA variants are slower than the standard schedule (down to -6.65% on Piledriver).
- MSVC builds, or projects that want a drop-in library: these are GNU extended inline-asm headers (GCC/Clang/MinGW) with no streaming API, build system or packaged releases.
- If OpenSSL is already linked and a 4-17% MD5 gain does not matter: the headline 5% and 23% are relative to the repo's own control schedule, not to OpenSSL.

## How it is fast

MD5 is one long dependency chain, so every trick moves the `b` input later in each round to shorten the critical path. G is computed as `(d & b) + (~d & c)`, so the `~d & c` half can be added to `a` before `b` is ready (G-function shortcut). With BMI1, `ANDN` saves a NOT and a MOV, and clausecker's identity rewrites I as a subtraction of `c ^ (~b & d)`. LEA can be replaced with two ADDs on Intel cores where three-operand LEA has 3-cycle latency, H-round MOVs are removed by reusing the XOR result, and input words can be cached in registers. On Intel, AVX-512VL `vpternlogd` computes F/G/H/I in one instruction and `vprold` rotates, both on a single xmm lane, which brings the critical path to 4 cycles per round (theoretical 4.0 cycles per byte vs 4.75 for the standard schedule).

## Compared with alternatives

Pick it over minio/md5-simd or gocrack's md5x8 when you need one MD5 stream as fast as possible: those siblings get their speedups by hashing 8-16 independent streams in SIMD lanes, which does nothing for a single file. Pick them for bulk multi-object hashing or cracking.

## Integration

| | |
|---|---|
| **Form** | header-only (inline-asm source-drop; md5.cpp is an example driver) |
| **Dependencies** | none (immintrin.h for the AVX-512 variant) |
| **Minimum toolchain** | GCC or Clang with GNU extended inline asm, C++11 (MD5_STATE is a template); benchmarked with Clang 11.0.0 -O3. -mbmi for GHBMI, -mbmi -mavx512vl for the AVX512 variant |
| **Platforms** | x86 (32-bit and x86-64; Cache4/Cache8/Cache8+G and AVX512 need x86-64, AVX512 needs AVX-512VL), 32-bit ARM (little and big endian), AArch64; only x86 is benchmarked |
| **Thread safety** | Reentrant by code reading: pure block functions on a caller-owned state, with no globals |
| **Drop-in for the baseline** | partial: digests are standard MD5, but there is no MD5_Init/Update/Final or EVP interface, so you write the buffering and padding wrapper (md5.cpp shows one) |

## Gotchas

- The README numbers were measured on commit e42661105 (December 2020), whose inline-asm operands have no early-clobber markers (0 '&' constraints vs 65 at HEAD). The author's own comment says compilers 'incorrectly clobber' operands. Commit b5cfafc 'Fix register clobbers' (2021-08-08) fixed every x86 variant and the AVX-512 one without changing instructions. The measured build relied on undefined register allocation that happened to work under Clang 11, and md5.cpp's known-answer tests only print 'TEST ERROR' and do not stop the benchmark. Later changes (REX-prefix avoidance and an AVX-512 tweak in 2023, the BMI1 variant in 2024) are not reflected in the published table. Copy current HEAD, not the benchmarked commit.
- Two harnesses: OpenSSL was read from `openssl speed md5` (16 KB, best of 3) and the variants from md5.cpp (calloc'd 16 KB zero buffer, 16384 hashes, best of 5). The author's 'Standard' control is sometimes faster than OpenSSL for reasons he says he does not know, so the gains over OpenSSL itself are 4-17% (derived from the chart's data table), not the 5-10% vs Standard quoted in prose.
- No variant wins everywhere. The best choice depends on the microarchitecture (LEA latency, rotate latency), so runtime dispatch or per-target builds are needed to get the quoted gains.
- The x86 headers assume little-endian input loads. Big-endian handling exists only in the ARM headers.

## Known shortcomings

- CPU model missing (microarchitecture only); percentages are against the author's own 'Standard' control, and the derived gain over OpenSSL is 4-17% scalar and about 26% with AVX-512 on Skylake-X (bench.png data table). Harness md5.cpp and Makefile (-O3 -static, Clang 11.0.0) are public.
- Enricher: the benchmarked commit e42661105 has zero early-clobber constraints (fixed in b5cfafc 'Fix register clobbers', 2021-08-08, no instruction change); md5.cpp known-answer failures only print while the benchmark keeps running; the README table predates the 2021-2024 code changes. Lead: FreeBSD libmd amd64 md5block.S (freebsd-src lib/libmd/amd64, Phabricator D45670: baseline, BMI1 and AVX-512 MD5 kernels).

## Caveats and trade-offs

The README's headline percentages are relative to the author's 'Standard' control, not to OpenSSL; OpenSSL's own readings are only in the chart image's data table, where Standard is sometimes faster than OpenSSL (Skylake-X, Piledriver, Jaguar) and sometimes slightly slower (K10, Airmont). OpenSSL was timed with its own `openssl speed` harness while the repo's variants were timed with md5.cpp (16 KB calloc'd zero buffer, 16384 rounds, best of 5, known-answer tests run first), so the two harnesses differ. CPUs are named by microarchitecture only, at locked frequency. No single variant wins everywhere: NoLEA is slower than Standard on Merom, Piledriver and Jaguar, and on Jaguar the best gain over OpenSSL is about 4%. The AVX512 variant was measured on Skylake-X only; the README says AMD Zen4's 2-cycle vector rotate makes it undesirable there. OpenSSL 1.1.1h dates from 2020 and is itself hand-written assembly, so there is no -O3 C reference comparison. The repo is a technique write-up with inline-asm headers (md5-x86-asm.h, md5-arm-asm.h, md5-arm64-asm.h) rather than a packaged library.

x86 variants are microarchitecture sensitive: plain NoLEA is slower than the control on Merom, Piledriver and Jaguar, and the AVX512 variant needs AVX512 (the author says AMD Zen4's 2-cycle vector bit-rotate latency makes AVX512 undesirable there, so only Intel AVX512 benefits). Single-buffer MD5 only; ARM and ARM64 headers exist but no ARM numbers are published. MD5 is cryptographically broken.

## Maintenance

Low-churn and copyable: Apache-2.0 OR MIT (licence files added 2026-09-17), last commit 2026-09-21, last code changes 2024-06 (BMI1 trick) and 2026-05 (AArch64 constraint fix), no open issues. The benchmark table dates from December 2020 and predates the 2021 clobber fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark: harness md5.cpp and Makefile (-O3 -static) are public and the compiler is Clang 11.0.0, but CPUs are named only by microarchitecture (Merom, Haswell, Skylake-X, Airmont, K10, Piledriver, Jaguar), never by CPU model, so it falls short of A. OpenSSL 1.1.1h readings appear in the README chart's data table next to the repo's own variants.
- **Verifier notes:** Numbers and quotes match the README. The record's caveat that no absolute OpenSSL numbers are printed was wrong: the chart's data table gives OSSL bytes/cycle for all seven CPUs, so gains over OpenSSL itself can be derived (4-17% for the best scalar variant, about 26% for AVX512 on Skylake-X). The benchmark harness md5.cpp and the Makefile are in the repo. Licence is Apache-2.0 OR MIT (LICENSE files added 2026-09-17); last commit 2026-09-21; 159 stars, 18 forks, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-72 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/animetosho/md5-optimisation>
  - <https://github.com/animetosho/md5-optimisation/commits>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/README.md>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/md5.cpp>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/Makefile>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/e42661105e971c94d0397e5b41bcf0a58e5874d3/Makefile>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/images/bench.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/README.md>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/md5.cpp>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/Makefile>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/md5-x86-asm.h>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/md5-arm-asm.h>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/HEAD/md5-arm64-asm.h>
  - <https://raw.githubusercontent.com/animetosho/md5-optimisation/e42661105e971c94d0397e5b41bcf0a58e5874d3/md5-x86-asm.h>
  - <https://github.com/animetosho/md5-optimisation/commits>
  - <https://github.com/animetosho/md5-optimisation/commit/b5cfafc9a98fd11003a4c313196e2376d97dc9de>
  - <https://github.com/animetosho/md5-optimisation/discussions/9>
  - <https://github.com/animetosho/md5-optimisation/issues>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libmd/amd64/md5block.S>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/animetosho/md5-optimisation`) · [data/wave13/enrich/raw/github_com_animetosho_md5_optimisation.json](../../../data/wave13/enrich/raw/github_com_animetosho_md5_optimisation.json) (enrichment confidence 0.8)

</details>
