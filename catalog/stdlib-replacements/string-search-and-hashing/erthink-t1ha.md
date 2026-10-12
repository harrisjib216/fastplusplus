# t1ha (Fast Positive Hash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Zlib` · 🔴 abandoned

> Portable C hash family (t1ha0/1/2) beating xxHash/Murmur on bulk throughput; modest edge on tiny keys.

| | |
|---|---|
| **Beats** | xxHash32 (also xxHash64 and the Murmur2/Murmur3 family) in SMHasher speed tests |
| **Claimed result** | Small keys (1-31 bytes, avg cycles/hash): t1ha_aes 33.03 and t1ha 35.55 vs xxHash32 43.72, which is \~1.32x and \~1.23x fewer cycles (derived from page data). Large keys (262144-byte block, MiB/s): t1ha_aes 34,636.42 and t1ha 12,228.80 vs xxHash32 5,513.55, i.e. \~6.3x and \~2.2x (derived from page data), or \~3.1x and \~1.1x vs xxHash64's 11,123.15 MiB/s (derived from page data). The \~6.3x/\~2.2x figures are bulk-throughput ratios, not small-key ones. |
| **Workload** | SMHasher speed tests from 2016 on an Intel Core i7-6700K (README 'Scores' tables): average cycles/hash over 1-31-byte keys and bulk MiB/s on a 262144-byte block, comparing t1ha / t1ha_aes against xxHash32/64, Murmur2/3, FNV1a, CRC32/64-HW, MUM, City/Farm/Metro/Spooky and others. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700K |
| **Compiler and flags** | gcc version 5.4.0 20160609 (Ubuntu 5.4.0-6ubuntu1\~16.04.4), CFLAGS: -march=native -O3 -fPIC |
| **Adoption** | 367 stars |
| **Last commit** | 2025-02-15 |
| **Links** | [repository](https://github.com/erthink/t1ha) · [benchmark](https://github.com/erthink/t1ha/blob/master/README.md) |

## Verdict

On SMHasher speed tests run in 2016 (GCC 5.4.0, -march=native -O3 -fPIC, Intel Core i7-6700K), t1ha_aes averaged 33.03 cycles/hash and t1ha 35.55 vs xxHash32's 43.72 over 1-31 byte keys (\~1.2-1.3x fewer cycles), while on a 262144-byte bulk block t1ha_aes reached 34,636 MiB/s and t1ha 12,229 MiB/s vs xxHash32's 5,514 MiB/s (\~6.3x/\~2.2x) and xxHash64's 11,123 MiB/s (\~3.1x/\~1.1x). The verification pass found the source record had mislabeled those bulk MiB/s figures as the 'small keys' result; the real small-key edge over xxHash32 is only \~1.2-1.3x.

## Use it when

- Bulk hashing of large buffers (KB+: checksums, content fingerprinting, dedup) on x86_64 with AES-NI, where the 2016 SMHasher bulk numbers show t1ha_aes far ahead of xxHash32/64
- Need a single API that gives both a 64-bit and a 128-bit digest via the same streaming context (t1ha2_init/update/final)
- Already a portable C (not C++) codebase, or need a C-callable hash with existing Rust/Erlang/Go/Kotlin bindings (linked from the README)
- Willing to vendor a small, frozen, Zlib-licensed source drop (3 .c files) since no upstream fixes are coming
- Mixed/heterogeneous CPU fleet where t1ha0's automatic best-available-implementation dispatch is worth its small indirection cost

## Skip it when

- Tiny keys (a few bytes to \~31 bytes) on a modern CPU: the maintainer's own later self-check (i7-4600U, GCC 9.3, in the README) shows t1ha2_atonce at 17.25 cycles/hash already behind xxhash32 (16.55), xxh3_64 (15.1) and wyhash_v7 (14.1) -- the 2016 small-key win over xxHash32 was only \~1.2-1.3x and has since been erased by newer hashes
- Cryptographic or adversarial-input use: the header explicitly states 't1ha' is 'Not suitable for cryptography'; no hash-flood resistance is claimed
- Need active upstream maintenance: GitHub deleted the author's account in 2022 and this repo is a restored read-only mirror; the true origin moved to GitFlic, whose current activity is unverified (a GitFlic fetch timed out during verification)
- Need std::hash-style implicit drop-in: t1ha is an explicit C function call with a seed argument, not something ADL or template specialization picks up automatically
- About to reach for t1ha0_32le/32be or t1ha0_ia32aes without checking the table: the author flags several dispatch targets ('alien' 32-bit/big-endian variants) as niche, and picking the wrong one can be slower than a portable hash

## How it is fast

The t1ha0_ia32aes_\* variants use AES-NI instructions for hardware-accelerated mixing (this is the 't1ha_aes' benchmark line); each AES-NI variant is compiled with its own flags (-maes plus -mavx/-mavx2 per meson.build) and t1ha0 picks among them, plus 32-bit and big-endian fallbacks, at runtime via T1HA0_RUNTIME_SELECT (optionally using GNU ELF indirect functions to cut call overhead). The core mixing uses a NH/UMAC-style multiply-add construction that the README's FAQ says was deliberately fixed to avoid the 'blinding multiplication' entropy-loss flaw it attributes to plain NH-family designs (and, per the README, to wyhash).

## Compared with alternatives

Pick t1ha over MUM/VMUM, rapidhash, komihash, or CityHash when you specifically want the AES-NI bulk-throughput path on x86, a plain-C (not C++) implementation with existing Rust/Go/Erlang/Kotlin ports, or a Zlib license; the MUM/VMUM sibling entry directly reports beating t1ha2, and rapidhash/komihash report better small-key numbers than xxHash on modern CPUs, so for tiny-key or newest-hardware workloads check those siblings first.

## Integration

| | |
|---|---|
| **Form** | source-drop (3 .c files from /src, or link as a static/shared lib via the provided Makefile/meson.build/vcxproj) |
| **Dependencies** | none (pure C, standard headers only: stdint.h, stddef.h, limits.h) |
| **Minimum toolchain** | C99 (meson.build passes -std=c99); README recommends GNU C 5.5+, Clang 5.0+, or MSVC 2017 15.6+ for proper performance, older GNU C / VS2013+ also supported |
| **Platforms** | any CPU with native 64-bit arithmetic (portable fallback); accelerated paths for x86/x86_64 (AES-NI, AVX/AVX2) and Elbrus/e2k; separate 32-bit little/big-endian and 64-bit big-endian variants exist but are marked non-primary |
| **Thread safety** | not documented explicitly; the hash functions are pure with no shared mutable state, and the streaming API uses a caller-allocated t1ha_context_t, so independent contexts are safe to use from different threads concurrently |
| **Drop-in for the baseline** | false -- explain: you call t1ha2_atonce(data, length, seed) (or t1ha1/t1ha0 equivalents) directly with an explicit seed, and must wrap it yourself to plug into std::hash-based containers |

## Gotchas

- t1ha0's chosen implementation depends on the host CPU's detected features, so its output is not guaranteed reproducible across machines; the README says t1ha0 results should only be used at runtime, never persisted or sent over a network -- use t1ha1/t1ha2 for stable, portable results
- t1ha2_atonce's 64-bit result and t1ha2_atonce128's 128-bit result are unrelated values (the 64-bit hash is not a truncation of the 128-bit one), per the header comment
- t1ha1 is documented to fail the strict avalanche criterion in some cases (per the README, discovered via Reini Urban's SMHasher fork); it is kept for compatibility but t1ha2 is the recommended, higher-quality successor
- The AES-NI variants need per-file compiler flags (-maes plus -mavx/-mavx2), not just runtime CPU detection -- building them without the matching flags for your toolchain silently loses the AES-NI path

## Known shortcomings

- Re-found by w7-mine-b under the old URL leo-yuriev/t1ha with the README Scores table (i7-6700K, gcc 5.4.0, -march=native -O3 -fPIC; 12228.80 MiB/s vs xxHash64 11123.15); the GitHub repo is an archived mirror and wyhash and xxh3 are faster on the same tables.

## Caveats and trade-offs

The benchmark data is from 2016 on a Skylake i7-6700K with GCC 5.4, and the exact SMHasher revision is not stated. The README's newer self-benchmark (make check, i7-4600U, GCC 9.3, flags unstated) shows t1ha2_atonce at 17.25 cycles/hash on 7-byte keys vs xxhash32 16.5, xxh3_64 15.1 and wyhash_v7 14.1, so t1ha2 is not faster on tiny keys against modern hashes; on 16 KiB keys t1ha2 (0.213 c/B) beats xxh3_64 (0.301) but roughly ties wyhash_v7 (0.206). The GitHub repo is an archived mirror: per the README, GitHub deleted the author's account in 2022, the repo was later restored read-only, and the origin moved to GitFlic. Compares against xxHash/Murmur, not std::hash.

t1ha_aes variant is non-portable (requires AES-NI); several other variants (t1ha_32le/be) are explicitly flagged by the author as 'alien' -- designed for niche 32-bit or big-endian targets, not general-purpose use; t1ha0 dispatches to the fastest available implementation at runtime, adding a small indirection cost.

## Maintenance

GitHub lists this repo as abandoned/archived, but per its own README that's because GitHub deleted the author's account in 2022 and this is a restored read-only mirror -- the stated true origin moved to GitFlic, whose activity level is unverified. Zlib-licensed and small (3 .c files), so it is cheap to vendor and self-maintain regardless.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** The README 'Scores' section states the CPU (i7-6700K), compiler (gcc 5.4.0) and CFLAGS (-march=native -O3 -fPIC). The numbers come from SMHasher, which is public (github.com/rurban/smhasher, which includes t1ha, as the README says), so tier A holds. The verdict is downgrade only because the claim was mislabeled and overstated.
- **Verifier notes:** The record paired MiB/s values (which are the 262144-byte bulk column, identical in both tables) with a 'small keys' label, overstating the small-key speedup (real \~1.2-1.3x vs xxHash32). The license is confirmed Zlib from the LICENSE file (GitHub spdx is NOASSERTION); stars 367, last commit 2025-02-15 and archived (abandoned) are accurate. I could not check the GitFlic origin (request timed out), so its activity is unverified.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline`, `caveats`
- **Shortcomings recorded by:** README Scores table (search agent, unverified)
- **Pages the verifier opened:**
  - <https://github.com/erthink/t1ha>
  - <https://github.com/erthink/t1ha/blob/master/README.md>
  - <https://github.com/erthink/t1ha/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/erthink/t1ha>
  - <https://github.com/erthink/t1ha/blob/master/README.md>
  - <https://github.com/erthink/t1ha/blob/master/t1ha.h>
  - <https://github.com/erthink/t1ha/blob/master/meson.build>
  - <https://github.com/erthink/t1ha/blob/master/LICENSE>
  - <https://github.com/erthink/t1ha/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/erthink/t1ha`) · [data/wave1/enrich/raw/github_com_erthink_t1ha.json](../../../data/wave1/enrich/raw/github_com_erthink_t1ha.json) (enrichment confidence 0.6)

</details>
