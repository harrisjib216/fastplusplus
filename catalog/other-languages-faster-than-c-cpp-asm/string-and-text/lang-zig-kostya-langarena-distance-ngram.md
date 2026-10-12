# Zig: LangArena Distance::NGram

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig std.AutoHashMap counting 4-grams; 1.58x faster than the best C/C++ build (libstdc++ std::unordered_map) in LangArena Distance::NGram.

| | |
|---|---|
| **Beats** | C++ using std::unordered_map&lt;uint32_t,int&gt; for 4-gram counts (g++ 16, clang++ 22); best C/C++ row is C++/Clang++/PGO at 0.822 s, C/Clang is 1.811 s |
| **Claimed result** | Zig 0.52 s (ReleaseSafe) vs C++/Clang++/PGO 0.822 s (best of the 16 C/C++ configurations), C++/G++/Fast 0.85 s (-O3 -march=native), C++/G++ 0.863 s and C++/Clang++ 0.877 s (prod, -O2), C/Clang 1.811 s: about 1.58x faster than the best C/C++ row and 1.66x faster than C++/G++ prod (derived from page data). Peak RSS 3.4 MB (C++ 6.6-7.1 MB). Zig/Unchecked (ReleaseFast) is 0.325 s; Rust 0.533 s, C#/JIT 0.516 s and Go 0.603 s also beat every C/C++ row. Earlier monthly runs show a steady lead: 1.50x on 2026-08-14, 1.46x on 2026-09-03, 1.41x on 2026-09-18 (Zig 0.16.0; derived from the results files). |
| **Workload** | For 10 generated string pairs (lengths 4 to 20,003 over a 10-letter alphabet), pack each 4-gram into a u32, count grams of the first string in one hash map and of the second in another while counting the intersection, and sum the overlap scores; 100 timed iterations. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78 GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37; the run's change note says the host moved from Ubuntu to Arch Linux) |
| **Compiler and flags** | C/C++ (c/Makefile, cpp/Makefile; versions from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu package build), libstdc++ (no -stdlib flag), -std=c++20 for C++. Headline 'prod' rows (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3, no -march). 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -ffast-math -fno-stack-protector -fomit-frame-pointer -fvisibility=hidden -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use (GCC). -flto=thin (Fast) and -flto=full (Unsafe) appear only in LDFLAGS while objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO rows were compared (instrumented PGO/Gen rows excluded). Zig: 0.17.0, 'zig build build-zig', which zig/build.zig maps to optimize = .ReleaseSafe (LLVM optimisation with runtime safety checks kept); the target comes from standardTargetOptions with no -Dtarget or -Dcpu in the build command, so it presumably builds for the host CPU (inference from zig/build.zig). The Zig/Unchecked row is ReleaseFast. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Zig's std.AutoHashMap is an open-addressing table with flat storage, while C++ std::unordered_map&lt;uint32_t,int&gt; allocates a node per distinct 4-gram, and the test builds two maps per string pair (this agent's inference from the containers used). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X (Linux), Zig 0.17.0 in ReleaseSafe took 0.52 s for 100 iterations. The best of the 16 C/C++ configurations, C++/Clang++/PGO (Clang 22.1.8 with libstdc++ std::unordered_map), took 0.822 s. C++/G++ at -O2 (GCC 16.0.1 snapshot) took 0.863 s and C/Clang with uthash took 1.811 s. Zig was about 1.58x faster than the best C/C++ row (derived from page data), and it led by 1.41-1.50x in the three earlier monthly runs on Zig 0.16.0.

## Use it when

- Zig code that builds many short-lived maps keyed by small integers, with the size known up front so ensureTotalCapacity avoids rehashing.
- As a data point when arguing to replace std::unordered_map&lt;uint32_t,...&gt; in a C++ counting loop with an open-addressing table: same algorithm and same pre-reserve, 1.58x from the container and language together.
- Memory-tight counting: Zig peaked at 3.4 MB RSS against 6.6-7.1 MB for the C++ rows (excluding instrumented PGO builds) and about 4 MB for C with uthash.
- When ReleaseSafe's bounds and overflow checks must stay on: the safe build still beat every one of the 16 C/C++ configurations, including -O3 -march=native and PGO.

## Skip it when

- Inside a C++ codebase: you cannot link this. Swap the container instead; absl::flat_hash_map or boost::unordered_flat_map would be the C++ analogue, but the suite never measured one, so the expected gain is an inference.
- Large or cache-hostile key sets: 10 letters give only 10,000 possible 4-grams, so each table stays in cache, and behaviour with millions of keys is not tested here.
- Delete-heavy workloads: std.HashMap deletes with tombstones, and its own doc comment warns that a map can become fragmented over time until it is rehashed.
- Concurrent updates: std.HashMap is not synchronized, and the benchmark is single-threaded.
- When raw speed matters more than safety checks: ReleaseFast reaches 0.325 s, and Rust's MaxPerf/Unsafe build reaches 0.382 s.

## How it is fast

The gap is the hash table. Zig's std.HashMap uses open addressing with linear probing: one metadata byte per slot (a 7-bit fingerprint and a used bit) checked before any key comparison, keys and values in flat arrays from one allocation, power-of-two capacity at a default 80% maximum load, and a Wyhash of the key bytes for AutoContext (hash_map.zig, last GitHub copy). ensureTotalCapacity(len) sizes each table from the string length, never from the distinct-gram count. The largest strings get 32,768 slots for at most 8,647 distinct keys (26% load), and the worst case is 63% (1,292 keys in 2,048 slots for the 1,382-character string), per my replay. There is no rehash during the loop and only two table allocations per call. libstdc++'s std::unordered_map&lt;uint32_t,int&gt; allocates one heap node per distinct key and maps a hash to a bucket with a modulo (_Mod_range_hashing returns __num % __den). That is 122,691 node allocations and frees per iteration in my replay, about 12.3 million in the timed loop. Zig wins even though it hashes every key with Wyhash while C++ uses the identity hash, which points at allocation and pointer chasing rather than hashing (inference). Safety checks cost 60%: ReleaseFast (Zig/Unchecked) runs the same code in 0.325 s against 0.52 s for ReleaseSafe.

## Compared with alternatives

Among the catalogued Distance::NGram rows, Zig ReleaseSafe (0.52 s, 3.4 MB) is level with C#/JIT (0.516 s, 40.6 MB) and ahead of Rust (0.533 s, 4.3 MB) and Go (0.603 s, 12.0 MB). Pick it when you want explicit allocators and the smallest footprint; its ReleaseFast build (0.325 s) is the fastest row in the suite. For string-keyed counting, see the Zig Etc::Words sibling.

## Integration

| | |
|---|---|
| **Form** | source-drop (Zig standard library only) |
| **Dependencies** | none (std.AutoHashMap; the benchmark executable links libc) |
| **Minimum toolchain** | Zig 0.17.0 as measured; the same source ran on Zig 0.16.0 in the August and September runs (0.567-0.575 s) |
| **Platforms** | any Zig target; measured on x86-64 Linux (AMD Ryzen 7 3800X), and build.zig's standardTargetOptions with no -Dcpu presumably builds for the host CPU |
| **Thread safety** | not documented for this code; std.HashMap has no locking (its SafetyLock only guards pointer stability in safe builds), and each call builds and frees its own two maps |
| **Drop-in for the baseline** | no |

## Gotchas

- Small, cache-resident workload: no map ever holds more than 8,647 keys, and every run computes the same per-run score of 3,312. My Python replay reproduces run.js's checksum 397440 as 120 runs (20 warm-up plus 100 timed), so all languages do the same work. It is not a large-key hash-map test.
- Part of the latest lead comes from the toolchain and host, not the code. Zig went from 0.567-0.575 s on Zig 0.16.0 (2026-08-14 to 2026-09-18) to 0.52 s on Zig 0.17.0 on 2026-10-05 with unchanged source, and that run also moved the host from Ubuntu to Arch Linux. The best C++ row moved between 0.805 and 0.848 s over the same runs, so the ratio drifted from 1.41x to 1.58x.
- In safe builds, getOrPut and ensureTotalCapacity lock and unlock a pointer-stability SafetyLock (hash_map.zig, last GitHub copy, which may differ from Zig 0.17.0), and every s1[i + 3] access is bounds-checked. That is part of the 0.52 s against 0.325 s gap between ReleaseSafe and ReleaseFast. The allocator is init.gpa from Zig's 'juicy main', and which implementation backs it in release builds is not documented in the sources reachable here; with two allocations per call it hardly matters.
- Harness check, no flaw found: the Zig, C and C++ harnesses reset the LCG, warm up for 20% of the iterations, reset again and time the loop with a monotonic clock, and the checksum is verified. The C++ loop bound s1.size() - 4 would underflow for strings shorter than 4 characters, which the generator never produces; Zig returns 0.0 early. Each configuration is measured once, with no variance figure.

## Known shortcomings

- 1.58x (0.52 vs 0.822 s, steady 1.4-1.6x over four monthly runs) from AutoHashMap against a node-based std::unordered_map; Rust, C# and Go win too; single run, Zig ReleaseSafe, C/C++ prod -O2 (the -O3 -march=native rows lose too).
- No harness flaw: checksum 397440 replays, and all languages do the same work on a small cache-resident workload (at most 8,647 keys per map, 122,691 node inserts per iteration). It is a container comparison (open-addressing AutoHashMap against node-based std::unordered_map), and the lead's growth from 1.41x to 1.58x came partly from the Zig 0.16 to 0.17 toolchain change and the Ubuntu to Arch host move with unchanged source.

## Caveats and trade-offs

Container comparison: a C++ open-addressing map (absl::flat_hash_map, boost::unordered_flat_map) would likely close the gap, and the suite only uses std::unordered_map (the C rows use uthash with a malloc per gram and are about 2x slower still). The Zig prod build is ReleaseSafe and presumably targets the host CPU (inference from zig/build.zig) against generic x86-64 C/C++ prod builds; the -march=native C/C++ rows still lose. Rust, C#, Go and others also beat C++ here, so the result is about std::unordered_map, not Zig. The C# row of this test is in the wave jitaot file. LangArena calls itself 'a subjective benchmark' and says AI tools helped translate the tests between languages. One measurement per test and configuration (no variance reported), although the harness checks each run's checksum against run.js. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3 -march=native Fast and Unsafe rows and the PGO rows also lose. Ratios are derived from the results file, not stated by the suite. Rows were picked as text tests where a non-C row beats every C and C++ row; most other text tests go the other way (Base64::Encode and Base64::Decode, where C is about 3x faster than Rust; Distance::Jaro is a tie). [retier] Enricher: no harness flaw (checksum 397440 replays; at most 8,647 keys per map, 122,691 node inserts per iteration, a small cache-resident workload). The lead's growth from 1.41x to 1.58x came partly from the Zig 0.16 to 0.17 toolchain change and the Ubuntu to Arch host move with unchanged source.

Flat hash tables use less memory per entry than node-based std::unordered_map.

## Maintenance

The MIT-licensed suite is active (41 stars, monthly reruns, last commit 2026-10-08 per the verifier), and the Zig NGram code has not changed since 2026-02-27. The routine is short and copyable, but the result says more about std::unordered_map than about Zig code generation, since Rust, C#, Go, Julia and others also beat every C++ row.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for both sides (zig/src/distance.zig NGram.ngramCalc, cpp/src/distance.cpp NGram::ngram, c/src/distance.c NGram_calc; workload in run.js), flags in zig/build.zig, cpp/Makefile and c/Makefile, and versions and the CPU (AMD Ryzen 7 3800X) in the results file. Both sides pack the same 4-grams into two pre-reserved standard hash maps and count the same intersection, so A stands (same precedent as the C# row of this test in batch-24).
- **Verifier notes:** Confirm at A: numbers match the Distance::NGram-runtime entries and the lead has held at 1.4-1.6x across four monthly runs; metadata checks out (MIT, 41 stars, last commit 2026-10-08). Shortcomings to record: a std::unordered_map versus open-addressing map comparison rather than a language win (Rust, C#, Go also win); single run per configuration; subjective, AI-assisted suite; headline C++ rows at -O2, though -O3 and PGO rows also lose; LTO flags inert.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-35 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/distance.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/distance.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/distance.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/main.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena/commits/master/zig/src/distance.zig>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/distance.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/distance.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/main.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/benchmark.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/helper.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/hash_map.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/start.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/process.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/README.md>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/hashtable_policy.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/kostya/langarena#distance-ngram`) · [data/wave14/enrich/raw/lang_zig_kostya_langarena_distance_ngram.json](../../../data/wave14/enrich/raw/lang_zig_kostya_langarena_distance_ngram.json) (enrichment confidence 0.75)

</details>
