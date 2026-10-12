# HighwayHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> SIMD-based keyed hash function; \~5x faster than SipHash at 1 KiB while keeping DoS-resistant strong-hash security claims.

| | |
|---|---|
| **Beats** | SipHash |
| **Claimed result** | At 1024 bytes: HighwayHashAVX2 0.24 cycles/byte vs SipHash 1.26 cycles/byte -&gt; \~5.25x faster (derived from page data, matching the README's own '5x faster' claim); at 64 bytes: HighwayHashAVX2 0.95 vs SipHash 1.93 -&gt; \~2x faster (derived from page data). |
| **Workload** | Hash inputs of 8, 31, 32, 63, 64, and 1024 bytes on a single idle core of a Xeon E5-2690 v3 (2.6GHz), comparing HighwayHashAVX2/SSE41 against SipHash, SipHash13, SipTreeHash and SipTreeHash13, measured in cycles/byte with a custom cycle-accurate nanobenchmark harness. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2690 v3, 2.6 GHz, single idle core |
| **Compiler and flags** | Patched GCC 4.9, 64-bit, flags -std=c++11 -O3 -march=haswell -fno-exceptions -fno-tree-vrp -fno-omit-frame-pointer -fno-strict-aliasing -fPIE (flags stated in the linked arXiv paper 1612.06257, Sec. 5; README says only 'patched GCC 4.9') |
| **Adoption** | 1,603 stars |
| **Last commit** | 2024-04-18 |
| **Links** | [repository](https://github.com/google/highwayhash) · [benchmark](https://github.com/google/highwayhash/blob/master/README.md) |

## Verdict

On a single idle core of an Intel Xeon E5-2690 v3 (2.6 GHz) compiled with a patched GCC 4.9, the README's own benchmark table shows HighwayHashAVX2 at 0.24 cycles/byte for 1024-byte inputs vs SipHash's 1.26 cycles/byte (\~5.25x) and 0.95 vs 1.93 cycles/byte at 64 bytes (\~2x), consistent with the linked arXiv paper's stated 5.2-5.3x speedup at 1 KiB.

## Use it when

- Hash-flooding-resistant hashing where a strong keyed hash faster than SipHash is needed, especially for inputs &gt;=64 bytes where the AVX2 speedup is largest
- x86-64 targets with AVX2 or SSE4.1, or POWER (VSX) / ARM/AArch64 (NEON) where the corresponding source file is included
- Applications that persist hashes long-term: output format is declared frozen forever, so stored hashes never break on upgrade
- Need 128- or 256-bit digests (checksums/integrity) from a single pass, not just a 64-bit hash
- Willing to vendor an archived Apache-2.0 source drop and pin a validated compiler rather than depend on a maintained package

## Skip it when

- Need a literal std::hash / std::unordered_map drop-in swap — HighwayHash needs explicit key management and its own state object, not a hasher functor substitution
- Target platform has none of AVX2/SSE4.1/VSX/NEON: falls back to a portable path the README says runs at \~10% of AVX2 throughput
- Building with a modern stock compiler without validating output first: open issue #94 (filed 2020, still open) reports a Portable-target hash mismatch on GCC 10.2, and the archived repo will never fix it
- Need the 'cryptographically strong' framing to hold at typical hash-table bin counts — the repo's own issue #28 is an unresolved dispute over that security claim
- Need active maintenance or security patching — GitHub shows the repository archived (read-only) and the hash output is explicitly frozen, so no further algorithmic or compiler-compat fixes will land

## How it is fast

Mixes input using SIMD 32x32-&gt;64-bit multiplies and permutes over a 1024-bit internal state held in AVX2/SSE4.1/VSX/NEON registers, with specialized handling of partial vectors for small inputs. The AVX2 build reaches 0.24 cycles/byte at 1024 bytes vs SipHash's 1.26, more than twice as fast as the repo's own SipTreeHash variant. A runtime dispatcher (instruction_sets.h) selects AVX2, SSE4.1, VSX, NEON, or a portable fallback at first use so one binary can exploit the widest available SIMD without recompiling.

## Compared with alternatives

Pick HighwayHash over komihash/MUM-hash/t1ha/rapidhash when the requirement is specifically SipHash's DoS-resistant strong-hash security framing plus multi-width (64/128/256-bit) SIMD output beating SipHash, not just the fastest possible non-cryptographic hashmap key hash; those sibling hashes target xxHash/CityHash/wyhash-class baselines for general-purpose hashing and are actively maintained, unlike this archived, output-frozen project.

## Integration

| | |
|---|---|
| **Form** | source-drop / static lib (Makefile and CMakeLists.txt build lib/libhighwayhash.a; CMake's BUILD_SHARED_LIBS option can produce a shared lib instead) |
| **Dependencies** | none beyond the C++ standard library; pthread is linked for the optional ThreadPool/profiling utilities, not required for hashing itself |
| **Minimum toolchain** | C++11 (Makefile and CMakeLists.txt both pass -std=c++11); CMake &gt;= 3.18 for the CMake build path; GCC/Clang new enough for AVX2/SSE4.1/NEON intrinsics as needed per target |
| **Platforms** | x86-64 (AVX2 or SSE4.1), ARM/AArch64 (NEON), POWER (VSX), plus a portable C++ fallback for any other architecture |
| **Thread safety** | not documented — HHState objects are stateful, constructed per hash, and the README/headers make no thread-safety claim; data_parallel.h's ThreadPool is for parallelizing benchmarks, not for sharing a hash state across threads |
| **Drop-in for the baseline** | partial — explain: same problem domain and a similar shape (keyed state object) as the repo's own SipHash implementation, but HighwayHash needs its own headers, a build step, and different key material, so it is not a std::hash-compatible swap |

## Gotchas

- Output is declared 'frozen forever' in the README: no future release will ever change existing hash values, but also none will ever improve speed or security further
- Intrinsics-using headers must be compiled into separate per-target translation units with matching flags (README 'Dispatch' section); mixing this up risks an ODR violation and crashes
- AVX2 carries a \~56K-cycle warmup penalty on Haswell-era CPUs per the README, so the authors recommend against AVX2 for infrequent/sporadic hashing in an otherwise non-AVX2 application
- Repository is GitHub-archived (read-only); open issue #94 (GCC 10.2 Portable-target hash mismatch, filed 2020) has no fix and, given the archival, never will

## Caveats and trade-offs

Compared against SipHash/SipTreeHash, not std::hash. Benchmark used a patched, non-public GCC 4.9 build (the paper notes unmodified GCC 6.3 gives \~10% lower throughput and GCC 4.8.4 \~3x slower code) on \~2014-era Haswell-EP hardware, and the GitHub repository is archived (last commit 2024-04-18), so the numbers do not reflect modern compilers or CPUs. The accompanying arXiv paper is a preprint, not peer-reviewed.

SIMD-dependent (AVX2/SSE4.1/VSX), needs runtime CPU dispatch for portability; the hash output is explicitly declared 'frozen forever' so no further algorithmic improvements will ever land; repository is archived by Google (read-only) so no future compiler/security fixes.

## Maintenance

Abandoned: the GitHub repo is archived (read-only), last commit 2024-04-18, and the hash output is explicitly declared frozen forever; it is Apache-2.0 licensed and small enough to vendor as a source drop, but pin and test the exact compiler version given the open, unresolved GCC 10.2 output-mismatch report (issue #94).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README 'Speed measurements' table shows HighwayHashAVX2 0.24 vs SipHash 1.26 cycles/byte at 1024 B and 0.95 vs 1.93 at 64 B, measured on a Xeon E5-2690 v3 with benchmark code in the repo (highwayhash/benchmark.cc + highwayhash/nanobenchmark.cc). The README omits flags, but the arXiv paper it links (1612.06257, Sec. 5) gives the compiler and exact flags, so all A criteria are met.
- **Verifier notes:** All README numbers match; the derived 5.25x (1 KiB) and \~2x (64 B) ratios are correct, and the paper itself says 5.2-5.3x vs SipHash at 1 KiB. Repo is archived with Apache-2.0 license and 1,603 stars; metadata is accurate.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/google/highwayhash>
  - <https://github.com/google/highwayhash/blob/master/README.md>
  - <https://github.com/google/highwayhash/blob/master/Makefile>
  - <https://arxiv.org/abs/1612.06257>
  - <https://arxiv.org/pdf/1612.06257>
- **Sources the enricher read:**
  - <https://github.com/google/highwayhash>
  - <https://github.com/google/highwayhash/blob/master/README.md>
  - <https://github.com/google/highwayhash/blob/master/highwayhash/highwayhash.h>
  - <https://github.com/google/highwayhash/blob/master/Makefile>
  - <https://github.com/google/highwayhash/blob/master/CMakeLists.txt>
  - <https://github.com/google/highwayhash/blob/master/highwayhash/highwayhash_target.h>
  - <https://github.com/google/highwayhash/issues/94>
  - <https://github.com/google/highwayhash/issues/28>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/google/highwayhash`) · [data/wave1/enrich/raw/github_com_google_highwayhash.json](../../../data/wave1/enrich/raw/github_com_google_highwayhash.json) (enrichment confidence 0.85)

</details>
