# SmolRapidhash (Unity/Burst port of rapidhash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> A single-file C#/Burst port of rapidhash V3 for Unity. On large buffers it is about 1.6-2.3x faster than Unity.Collections' Burst xxHash3.

| | |
|---|---|
| **Beats** | xxHash (XXH3, via Unity.Collections xxHash3) |
| **Claimed result** | Readme text: rapidhash reaches about 38 GB/s on Ryzen 5950X and about 67 GB/s on Apple M4 Max; 'Rapidhash is always faster than xxhash (XXH3)'. Read from the readme chart images (approximate): Ryzen 5950X plateau, Burst rapidhash \~38 GB/s vs Burst XXH3 \~23.5-24.5 GB/s; native XXH3 \~37.5-38 GB/s, about equal to rapidhash from 16 KB up. M4 Max: native rapidhash \~68-73 GB/s, Burst rapidhash \~63-68 GB/s, native XXH3 \~49-50 GB/s, Burst XXH3 \~28-29 GB/s. |
| **Workload** | Unity editor benchmark (Assets/HashBenchmark.cs) hashing large buffers, comparing native C rapidhash, Burst-compiled C# rapidhash port, native C XXH3, and Burst-compiled C# XXH3 (Unity.Collections). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5950X (Windows); Apple M4 Max (macOS) |
| **Compiler and flags** | Native C (upstream rapidhash/xxhash bench program): Visual Studio 2022 (17.14.23) on Windows, Xcode 16.1 on macOS, flags not stated. C# port: Unity 2022.3 (ProjectVersion 2022.3.62f3) and Unity 6.3, Burst (1.8.23 in packages-lock.json), run in the editor from a non-Burst C# script; Burst options not stated. |
| **Adoption** | 17 stars |
| **Last commit** | 2026-03-07 |
| **Links** | [repository](https://github.com/aras-p/UnitySmolRapidhash) · [benchmark](https://github.com/aras-p/UnitySmolRapidhash/blob/main/readme.md) |

## Verdict

The author's editor harness (Assets/HashBenchmark.cs, the large-input part of the xxHash/rapidhash bench, 256 B to 128 MB, best-of-rounds MB/s) compared Burst rapidhash with Unity.Collections' Burst xxHash3 in Unity 2022.3 and 6.3. It adds native C numbers from the upstream bench, built with VS 2022 17.14.23 on the Ryzen 5950X and Xcode 16.1 on the M4 Max (flags unstated). Read from the charts, Burst rapidhash plateaus near 38 vs 24 GB/s on the Ryzen and 63-68 vs 28-29 GB/s on the M4 Max. Against native C XXH3 it only ties from 16 KB up on the Ryzen (and trails beyond 32 MB), and on the M4 Max it only wins from about 2-8 KB up, depending on Unity version, so 'always faster' holds only Burst-vs-Burst.

## Use it when

- Content hashing of large buffers inside Unity (mesh/texture/asset bytes, serialized blobs, cache or dedup keys of 1 KB and up), where you would otherwise call Unity.Collections xxHash3.Hash64.
- Apple Silicon, where the gap is largest: on the M4 Max chart, Burst rapidhash plateaus around 63-68 GB/s vs about 28-29 GB/s for Burst XXH3.
- Burst jobs that need an allocation-free, stateless 64-bit non-cryptographic hash over NativeArray or raw pointers.
- Matching hashes produced by native C/C++ tooling that calls rapidhash V3's default `rapidhash()` with seed 0. By code comparison the port follows upstream, but no test vectors ship with it.

## Skip it when

- Small keys (ints, small structs, short strings for NativeHashMap): nothing under 256 B was benchmarked. At 256 B, Burst rapidhash reaches only about 10-16 GB/s, against about 26 GB/s for native C rapidhash on the Ryzen.
- Hashing untrusted input (server-side player data): there is no seed parameter and the secrets are fixed public constants, so the published seed-independent collisions for inputs over 16 bytes apply directly.
- Streaming or incremental hashing, 128-bit output, or the rapidhash micro/nano variants: only the one-shot 64-bit function is ported.
- Buffers far larger than cache on x86: from 32 MB up, everything is memory-bound (about 19-22 GB/s), and native XXH3 is slightly ahead at 64-128 MB on the Ryzen 5950X.
- Projects that need a maintained, tested dependency: 8 commits made in one day, version 0.1.0, no tests and no issue history.

## How it is fast

It is the wyhash-family folded multiply (MUM): a 64x64-&gt;128-bit multiply with the halves XORed. The multiply comes from Burst's `Common.umul128` intrinsic, so each 16 input bytes cost one native `mul`. Inputs over 112 bytes run 7 independent multiply lanes per 112-byte block for instruction-level parallelism. Inputs of 16 bytes or less use two overlapping unaligned reads and one final mix. Unity.Collections' XXH3 port, by the author's account, runs 30-40% below native C, and this port does not show that penalty.

## Compared with alternatives

It is the only catalogued rapidhash/XXH3-class hasher that runs as plain Burst C# inside Unity. The C xxHash/wyhash/rapidhash libraries and the Rust crates (hoxxep rapidhash, foldhash, gxhash) need a native plugin, which gives better small-input speed if you can ship one. Pick it over Unity.Collections' built-in xxHash3 when inputs are about 1 KB or larger and you need neither seeds nor streaming.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | com.unity.burst (1.8.23 in the lock file) for Common.umul128; engine Unity.Collections.LowLevel.Unsafe/NativeArray; 'allow unsafe code' enabled |
| **Minimum toolchain** | Unity 2022.3 (benchmarked 2022.3.62f3 and 6.3) with Burst 1.8.23; package.json declares unity 6000.0 |
| **Platforms** | little-endian only, per the source header; benchmarked only on Windows x64 (Ryzen 5950X) and macOS arm64 (M4 Max); other Burst targets not documented |
| **Thread safety** | Stateless static functions with no shared data, so safe to call concurrently. Not documented explicitly. |
| **Drop-in for the baseline** | partial — the call shape matches Unity.Collections xxHash3.Hash64(ptr, len), but it returns ulong instead of uint2, takes no seed, and produces different hash values, so stored XXH3 hashes do not carry over. |

## Gotchas

- `Hash64<T>(ref T)` and the array/span overloads hash the raw bytes of T, including any struct padding. Values that compare equal can hash differently unless padding is deterministic.
- Only `Hash64(void*, long)` carries [BurstCompile]. Performance when Burst compilation is disabled or unavailable is not documented, and the umul128 intrinsic is the reason Burst is required.
- package.json requires unity 6000.0 but the repo's project is 2022.3.62f3. On 2022.3, copy SmolRapidhash3.cs instead of installing the package.
- The benchmark calls into Burst through a delegate from a non-Burst MonoBehaviour, and small sizes include that overhead. Unity 6.3 is noticeably faster than 2022.3 below 8 KB, for example about 16 vs 8 GB/s at 256 B on the M4 Max.

## Known shortcomings

- No compiler flags stated and the native benchmark harness is not in the repo; XXH3 comparison exists only as chart PNGs, where native XXH3 about ties rapidhash on Ryzen at 16 KB and above.
- 'Always faster' holds only Burst-vs-Burst; against native C XXH3 it ties on Ryzen at 16 KB and above, trails above 32 MB, and on M4 wins only from \~2-8 KB up. Nothing under 256 B benchmarked. No seed, public secrets, no streaming or 128-bit output. One-day v0.1.0 with no tests or test vectors; matches upstream rapidhash rev 92731ee by code reading only.

## Caveats and trade-offs

Small single-purpose port (17 stars; all 8 commits on 2026-03-07); the readme does not say it is finished. The harness is a plain C# editor script that the author notes may add overhead. The Burst-vs-Burst gap partly reflects Unity.Collections' XXH3 port, which the author says is 30-40% slower than native C XXH3. Against native XXH3 on the Ryzen 5950X, rapidhash only ties at 16 KB and above, and native XXH3 is slightly ahead at 32-128 MB, despite the 'always faster' line. The native harness is not in this repo.

Requires Unity + Burst compiler and unsafe C#; core port is \~100 lines but only usable inside a Unity/Burst project, not a general-purpose C++ library.

## Maintenance

A one-day project (all 8 commits on 2026-03-07, v0.1.0, 17 stars, no issues) that is not otherwise maintained. It is MIT-licensed and one short C# file, so treat it as a reviewed snippet to vendor rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The readme's charts compare rapidhash against native C XXH3 and Unity.Collections' Burst xxHash3 on a Ryzen 5950X and an M4 Max. The Burst side's harness is public (Assets/HashBenchmark.cs), and VS 2022 17.14.23, Xcode 16.1 and the Unity 2022.3/6.3 versions are named. No compile flags are given, for either the native build or the Burst/editor settings. The native numbers come from the upstream Nicoshev/rapidhash bench program, which is not in this repo. First-party with partial methodology: C.
- **Verifier notes:** Only the 38 and 67 GB/s figures are in the readme text; every XXH3 value comes from the two chart PNGs, which I opened and read. maintenance_status changed from 'finished' to 'active': the last commit is 2026-03-07 (under 12 months old) and I found no completion statement. License MIT (LICENSE file, spdx MIT) is confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/readme.md>
  - <https://github.com/aras-p/UnitySmolRapidhash>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/readme.md>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/shot-graph-ryzen5950x.png>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/shot-graph-m4max.png>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/Assets/HashBenchmark.cs>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/Packages/org.nesnausk.smol-rapidhash/Scripts/SmolRapidhash3.cs>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/Packages/packages-lock.json>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/ProjectSettings/ProjectVersion.txt>
  - <https://api.github.com/repos/aras-p/UnitySmolRapidhash>
  - <https://api.github.com/repos/aras-p/UnitySmolRapidhash/commits?per_page=10>
- **Sources the enricher read:**
  - <https://github.com/aras-p/UnitySmolRapidhash>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/readme.md>
  - <https://api.github.com/repos/aras-p/UnitySmolRapidhash>
  - <https://api.github.com/repos/aras-p/UnitySmolRapidhash/commits?per_page=20>
  - <https://api.github.com/repos/aras-p/UnitySmolRapidhash/git/trees/HEAD?recursive=1>
  - <https://github.com/aras-p/UnitySmolRapidhash/issues>
  - <https://github.com/aras-p/UnitySmolRapidhash/pulls>
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/Packages/org.nesnausk.smol-rapidhash/Scripts/SmolRapidhash3.cs>
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/Assets/HashBenchmark.cs>
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/Packages/org.nesnausk.smol-rapidhash/package.json>
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/Packages/org.nesnausk.smol-rapidhash/SmolRapidhash.asmdef>
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/Packages/manifest.json>
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/Packages/packages-lock.json>
  - <https://github.com/aras-p/UnitySmolRapidhash/blob/main/ProjectSettings/ProjectVersion.txt>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/shot-graph-ryzen5950x.png>
  - <https://raw.githubusercontent.com/aras-p/UnitySmolRapidhash/main/shot-graph-m4max.png>
  - <https://raw.githubusercontent.com/Nicoshev/rapidhash/92731ee/rapidhash.h>
  - <https://liams.website/articles/seed-independent-collisions-on-wyhash-and-rapidhash>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/aras-p/unitysmolrapidhash`) · [data/wave7/enrich/raw/github_com_aras_p_unitysmolrapidhash.json](../../../data/wave7/enrich/raw/github_com_aras_p_unitysmolrapidhash.json) (enrichment confidence 0.75)

</details>
