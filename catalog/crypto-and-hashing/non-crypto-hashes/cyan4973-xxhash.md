# xxHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-2-Clause (library xxhash.c/xxhash.h); xxhsum CLI is GPL-2.0-or-later` · 🟢 active

> SIMD-vectorized non-cryptographic hash family; XXH3 beats CityHash \~2.7x on in-RAM buffer bandwidth.

| | |
|---|---|
| **Beats** | CityHash |
| **Claimed result** | XXH3 (AVX2) 59.4 GB/s vs City64 22.0 GB/s (\~2.7x) and City128 21.7 GB/s (\~2.7x), both derived from page data; also vs MurmurHash Murmur3 (32-bit) 3.9 GB/s (\~15.2x, derived from page data; note Murmur3 row is the 32-bit variant, so not a perfectly matched width comparison against XXH3's 64/128-bit output). Small-data velocity: XXH3 133.1 vs City64 76.6, vs Murmur3 56.1. |
| **Workload** | Bandwidth (GB/s) and small-data velocity of hashing in-RAM buffers, measured with the project's open-source bench program (tests/bench). |
| **Metric** | throughput |
| **Hardware** | Intel i7-9700K, Ubuntu x64 20.04 |
| **Compiler and flags** | Clang v10.0, -O3 (tests/bench/Makefile also defines a benchHash_avx2 target that adds -mavx2) |
| **Adoption** | 11.3k stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/Cyan4973/xxhash) · [benchmark](https://github.com/Cyan4973/xxhash) |

## Verdict

Project's own tests/bench program (Clang v10.0, -O3, Intel i7-9700K, Ubuntu 20.04 x64) measured XXH3 (AVX2) at 59.4 GB/s versus CityHash64 at 22.0 GB/s (\~2.7x) and CityHash128 at 21.7 GB/s (\~2.7x); versus Murmur3 (32-bit) at 3.9 GB/s (\~15.2x, not width-matched). Small-data velocity: XXH3 133.1 vs City64 76.6 vs Murmur3 56.1.

## Use it when

- Non-cryptographic hashing of in-RAM buffers where throughput dominates (checksums, hash tables, dedup, content-addressing)
- Hot loops hashing small/fixed-length keys, using XXH_INLINE_ALL for compile-time-constant lengths
- Need identical hash output across little/big-endian and 32/64-bit platforms
- Embedded or constrained targets: XXH32 for 32-bit-only hardware, or XXH_NO_STDLIB to avoid malloc/free
- Want SIMD speedup across x86 (AVX2/AVX512), ARM (NEON), POWER (VSX), or RISC-V (RVV) without hand-writing per-ISA paths

## Skip it when

- Cryptographic use cases (signatures, password storage, adversarial-input integrity) - README explicitly says do not use xxHash for these
- Comparing against 32-bit-only hashes and expecting a width-matched number: the project's own Murmur3 benchmark row is the 32-bit variant, not matched to XXH3's 64/128-bit output
- Raw single-thread bandwidth is the only criterion and the \~1.09x edge of wyhash (per catalog sibling entry) matters more than xxHash's broader platform/test-suite maturity
- Distributing the xxhsum CLI where GPL-2.0-or-later is unacceptable (the library itself, xxhash.c/xxhash.h, is BSD-2-Clause and unaffected)
- Need statically-allocated streaming state guaranteed correct with zero further testing: the streaming API has had real bugs in the past (see gotchas), now fixed but worth pinning a recent release

## How it is fast

XXH3 uses vectorized arithmetic (SSE2/AVX2/AVX512/NEON/VSX/RVV/LoongArch LSX-LASX, auto-selected at compile time or runtime-dispatched) with multiply-and-fold mixing tuned for both large-buffer bandwidth and small-key latency. XXH_INLINE_ALL header-only mode lets the compiler inline and constant-fold hashing when key length is a compile-time constant, reported at roughly +200% for small keys. Optional runtime ISA dispatch (Makefile DISPATCH=1 / LIBXXH_DISPATCH=1) picks the best available vector unit at startup instead of requiring a fixed -m flag at build time.

## Compared with alternatives

wyhash edges out XXH3 by roughly 1.09x bandwidth per the catalog sibling entry, but xxHash documents wider SIMD/architecture coverage (SSE2/AVX2/AVX512/NEON/VSX/RVV/LoongArch), a dedicated massive collision tester plus SMHasher pass, and a mature package ecosystem (vcpkg, Repology-tracked distro packages); pick xxHash when portability across architectures and test-suite maturity outweigh a single-digit-percent throughput gap.

## Integration

| | |
|---|---|
| **Form** | source-drop (xxhash.c + xxhash.h); also buildable as static/shared libxxhash, or header-only via XXH_INLINE_ALL |
| **Dependencies** | none required; optional use of stdlib.h (malloc/free, disable via XXH_NO_STDLIB) and string.h (memcpy/memset/memcmp, redirectable via XXH_memcpy/XXH_memset/XXH_memcmp macros) |
| **Minimum toolchain** | C90 (ANSI C) baseline with optional C99/C++11 feature detection; compiles cleanly as C++ via an extern "C" guard (disable with XXH_NO_EXTERNC_GUARD) |
| **Platforms** | x86/x64 (scalar, SSE2, AVX2, AVX512, runtime-dispatchable), aarch64/ARM (NEON), PowerPC (VSX), RISC-V (RVV), LoongArch (LSX/LASX), plus a portable scalar fallback everywhere; produces identical hashes on little- and big-endian systems |
| **Thread safety** | not documented explicitly. One-shot calls (XXH32/XXH64/XXH3_64bits, etc.) are stateless and reentrant. XXH32_state_t/XXH64_state_t/XXH3_state_t streaming objects are not described as synchronized - do not share one state object across threads without external locking |
| **Drop-in for the baseline** | partial — same one-shot/streaming call shape as CityHash but different function names (XXH3_64bits/XXH3_128bits vs CityHash64/CityHash128); call sites need updating |

## Gotchas

- Explicitly not a cryptographic hash - README warns against signatures, password storage, or adversarial-integrity use
- Peak AVX2/AVX512 throughput needs either the matching -m compiler flag or Makefile DISPATCH=1/LIBXXH_DISPATCH=1 runtime dispatch; a naive build can silently run at scalar/SSE2 speed
- Streaming API has a history of real bugs: issue #816 "Streaming hashing is broken" (2023) and #378 "Uneven chunk size in xxh3 stream computes wrong hash" (2020), both closed/fixed but signal the incremental path is the more fragile part of the API
- XXH_FORCE_ALIGN_CHECK / XXH_FORCE_MEMORY_ACCESS build macros exist because some architectures need a different memory-access strategy for best performance; the defaults are auto-selected per architecture and may need tuning on unusual targets

## Caveats and trade-offs

First-party benchmark (the project's own tests/bench program), but it states the methodology, compiler, flags and CPU in full, which meets Tier A. The table has no std::hash row; the nearest stdlib-style entry is FNV64 at 1.2 GB/s. The Murmur3 row is the 32-bit variant, so it is not width-matched against XXH3's 64-bit output. GitHub reports the license as NOASSERTION because the repo mixes licenses: the library is BSD-2-Clause and the xxhsum CLI is GPLv2-or-later.

XXH3/XXH128 use vectorized (SSE2/AVX2) code paths so peak numbers depend on target ISA; not a cryptographic hash (explicitly documented); 32-bit XXH32 exists for constrained targets but is far slower than XXH3.

## Maintenance

Actively maintained (last commit 2026-09-20, 11.3k stars, CHANGELOG shows ongoing RISC-V/LoongArch perf work); library (xxhash.c/xxhash.h) is BSD-2-Clause and trivially vendorable, while the separate xxhsum CLI is GPL-2.0-or-later.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks table sets XXH3 against City64 and City128, Murmur3, FNV64 and others. It states an Intel i7-9700K on Ubuntu 20.04, Clang v10.0 and -O3, and the benchmark code is public at tests/bench (benchHash.c, Makefile with CFLAGS ?= -O3).
- **Verifier notes:** Every number and ratio checks out against the README table (59.4/22.0 gives \~2.7x, 59.4/3.9 gives \~15.2x). GitHub's spdx_id is NOASSERTION; the LICENSE file shows BSD-2-Clause for the library, and cli/xxhsum.c is GPLv2-or-later, so it stays copyable. I removed from the caveats the speculative claim that std::hash gaps 'track the Murmur3 row'. Metadata checks out: 11,283 stars, last commit 2026-09-20.
- **Fields the verifier corrected:** `license`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Cyan4973/xxhash>
  - <https://github.com/Cyan4973/xxHash/blob/dev/LICENSE>
  - <https://github.com/Cyan4973/xxHash/tree/dev/tests/bench>
  - <https://github.com/Cyan4973/xxHash/blob/dev/tests/bench/Makefile>
  - <https://github.com/Cyan4973/xxHash/blob/dev/cli/xxhsum.c>
- **Sources the enricher read:**
  - <https://github.com/Cyan4973/xxhash>
  - <https://github.com/Cyan4973/xxHash/blob/dev/README.md>
  - <https://github.com/Cyan4973/xxHash/blob/dev/xxhash.h>
  - https://github.com/Cyan4973/xxHash (recursive tree listing)
  - <https://github.com/Cyan4973/xxHash/blob/dev/CHANGELOG>
  - <https://github.com/Cyan4973/xxHash/blob/dev/SECURITY.md>
  - <https://github.com/Cyan4973/xxHash/issues?q=label%3Abug>
  - <https://github.com/Cyan4973/xxHash/blob/dev/LICENSE>
  - <https://github.com/Cyan4973/xxHash/tree/dev/tests/bench>
  - <https://github.com/Cyan4973/xxHash/blob/dev/tests/bench/Makefile>
  - <https://github.com/Cyan4973/xxHash/blob/dev/cli/xxhsum.c>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/cyan4973/xxhash`) · [data/wave0-seed/enrich/raw/github_com_cyan4973_xxhash.json](../../../data/wave0-seed/enrich/raw/github_com_cyan4973_xxhash.json) (enrichment confidence 0.88)

</details>
