# fastfilter (hexops)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT OR Apache-2.0` · 🟢 active

> Zig binary fuse and xor filters; binary fuse builds 1.7-3.8x faster than xor, with smaller filters and equal lookups.

| | |
|---|---|
| **Beats** | xor filter |
| **Claimed result** | 2019 MacBook Pro (2.3 GHz 8-core Intel Core i9): binaryfuse8 builds a 1M-key filter in 37.5 ms vs 103.4 ms for xor8 (\~2.8x) and a 100M-key filter in 7.4 s vs 28.0 s (\~3.8x). Ryzen 9 3900X: 44.6 ms vs 76.0 ms at 1M (\~1.7x) and 6.9 s vs 19.1 s at 100M (\~2.8x). Ratios are derived from page data. contains() is about the same as xor8 (24.0 vs 25.0 ns at 1M and 145 vs 153 ns at 100M on the Mac). binaryfuse8 uses 9.04 vs 9.84 bits/key and 22 vs 52 MiB peak build memory at 1M. |
| **Workload** | populate() and contains() on 1M-100M random u64 keys, comparing binaryfuse8/16/32 vs xor2/4/8/16/32 vs fuse (Zig implementation, zig run -O ReleaseFast src/benchmark.zig) |
| **Metric** | throughput |
| **Hardware** | 2019 MacBook Pro, 2.3 GHz 8-core Intel Core i9, 16 GB 2667 MHz DDR4; also Windows 10, 3.79 GHz AMD Ryzen 9 3900X, 32 GB 2133 MHz DDR4 |
| **Compiler and flags** | zig run -O ReleaseFast src/benchmark.zig -- --xor 8 --num-keys N; Zig 0.12.0-dev.706+62a0fbdae |
| **Adoption** | 293 stars (archived GitHub mirror; project now self-hosted on Forgejo) |
| **Last commit** | 2026-04-11 |
| **Links** | [repository](https://code.hexops.org/hexops/fastfilter) · [benchmark](https://code.hexops.org/hexops/fastfilter/raw/branch/main/README.md) |

## Verdict

The README's own harness (src/benchmark.zig, Zig 0.12.0-dev.706, -O ReleaseFast) builds over consecutive keys 0..N-1 and probes random, nearly all-miss u64s. On a 2019 MacBook Pro (2.3 GHz 8-core Core i9), BinaryFuse8 populates 1M/100M keys in 37.5 ms/7.4 s vs 103.4 ms/28.0 s for Xor8 (\~2.8x/\~3.8x); on a Ryzen 9 3900X the gaps are \~1.7x/\~2.8x, and lookups tie. Both sides are this library's own Zig code, with nothing measured against the C reference, Bloom or cuckoo filters, and the tables predate the current benchmark.zig, which drops the fuse rows and parses only --num-trials.

## Use it when

- A Zig codebase that needs a read-only membership pre-check (a skip-the-disk or skip-the-network test) over a key set that is rebuilt in batches rather than updated.
- Build time and build memory matter: BinaryFuse8 populated 1M keys in 37.5 ms vs 103.4 ms for Xor8 and 100M in 7.4 s vs 28.0 s (2019 MacBook Pro), using roughly 23 vs 55 bytes/key of scratch.
- You want about 0.39% false positives at about 9.0 bits/key (BinaryFuse8). BinaryFuse(u16) gives about 0.0015% at 18 bits/key, and BinaryFuse(u32) gives effectively zero at 36 bits/key.
- The key set is too large to keep as a contiguous array: populateIter streams keys from any iterator. You can also give the filter storage and the build scratch separate std.mem.Allocator instances, for example an mmap-backed one for scratch.

## Skip it when

- You need inserts, deletes or incremental growth: the filters are immutable, so use a cuckoo or quotient filter instead.
- You expect faster lookups than an xor filter: contains() measured 24.0 vs 25.0 ns at 1M keys and 145 vs 153 ns at 100M. At 10M+ keys with 16/32-bit fingerprints, lookups cost 100-175 ns, dominated by 3 random memory loads.
- You are not writing Zig: the library exports no C ABI. Use FastFilter/xor_singleheader for C/C++, xorf for Rust or FastFilter/xorfilter for Go. For 100M+ key xor builds, the README itself points to the C library's xor8_buffered_populate, which is not implemented here.
- Memory-tight or huge builds: peak build scratch for BinaryFuse8 is about 2 GiB at 100M keys, on top of the finished filter (and the keys, unless you stream them). init() computes the slot count as a u32, so a single filter tops out at about 3.8 billion keys.
- You need minimum space or a stable toolchain. Arity is hard-coded to 3, so the 4-wise variant that the paper puts within 8% of the lower bound is not available, and ribbon filters such as BuRR get closer. The code also tracks Mach-nominated Zig nightlies, currently 0.16.0-dev.

## How it is fast

Binary fuse filters (Graf & Lemire, arXiv 2201.01174) map each key to 3 slots in three consecutive power-of-two segments, a spatially coupled 'fuse' layout after Dietzfelbinger & Walzer. That lets the array hold about 1.125n slots instead of the xor filter's 1.23n (9.0 vs 9.84 bits/key at 8-bit fingerprints). Construction groups hashes by segment (high hash bits), peels the 3-hypergraph with a queue of cells hit by a single key and assigns fingerprints in reverse. Its per-slot scratch is a 1-byte count, an 8-byte xor-of-hashes and a 4-byte queue entry, vs xor's 16-byte sets plus 16-byte queue and stack entries, hence 22 vs 52 MiB peak at 1M keys. A query is one murmur64 mix, a 64x64-&gt;128 multiply-high and 3 XORed loads, the same work as an xor filter, so lookups tie.

## Compared with alternatives

Pick it when your code is Zig and you want iterator-based population with separate filter and scratch allocators. Otherwise use a sibling: FastFilter/xor_singleheader (the C reference it ports, which also has buffered xor construction) for C/C++, xorf for Rust, FastFilter/xorfilter for Go, and BuRR or a ribbon filter when bits/key matters more than build speed.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Zig std only) |
| **Minimum toolchain** | Zig 2026.4.10-mach (identical to 0.16.0-dev.3142+5ccfeb926), per build.zig.zon's mach_zig_version and meant to be installed via anyzig. benchmark.zig uses std.Io and std.process.Init, so older Zig will not build the whole package. The last tag, v0.11.0, targets Zig 0.12.0-dev.706. |
| **Platforms** | Any Zig target: pure scalar Zig with no SIMD or intrinsics (it uses a u128 multiply-high). The CI config targets Linux x86-64 only, and the README benchmarks ran on macOS and Windows x86-64. |
| **Thread safety** | Not documented. By inspection, contain() takes \*const Self and writes nothing, so concurrent lookups on a built filter look safe. populate() mutates the filter and uses caller-provided scratch. |
| **Drop-in for the baseline** | partial — inside this library, BinaryFuse(T) has the same init/populate/populateIter/contain/deinit/sizeInBytes API as Xor(T), so switching is a one-line type change. The serialized fields differ (segment fields instead of blockLength), and it is not a drop-in for the C xor_singleheader or any non-Zig code. |

## Gotchas

- The README install snippet uses github.com/hexops/fastfilter/archive/\$LATEST_COMMIT.tar.gz, but the archived GitHub repo's HEAD now contains only a README saying 'Moved to https://code.hexops.com/hexops/fastfilter' (which 301s to code.hexops.org). Point build.zig.zon at the Forgejo repo instead. The README's exe.addModule build snippet also predates the current build API.
- Xor(T) requires unique keys and returns error.KeysLikelyNotUnique after 100 seeds otherwise; run AutoUnique first. BinaryFuse(T) deduplicates automatically.
- Custom populateIter iterators must return null at the end and then restart from the first key, because construction rescans on every seed retry. This is enforced only in Debug builds (a panic); ReleaseFast does not check it.
- Seeds come from a fixed SplitMix64 starting constant, so builds are deterministic and the caller cannot supply a seed. Calling populate() with zero keys returns before the seed or fingerprints are set, so contain() on an empty BinaryFuse reads uninitialized allocator memory. The tests pass only because page_allocator returns zeroed pages.

## Known shortcomings

- The real ratio is \~3.8x (28.0 vs 7.4), not \~19x, and both sides are its own Zig code; the published tables were made with Zig 0.12-dev and the bench code has since been ported; the GitHub repo is archived (moved to Forgejo).
- No comparison against the C reference, Bloom or cuckoo filters; the win is build speed and memory (22 vs 52 MiB at 1M keys) while lookups tie. Bench keys are sequential 0..N-1 with probes that are nearly all misses; the current benchmark.zig drops fuse rows and ignores --xor/--num-keys. The README install URL points to a GitHub mirror that now holds only a 'Moved' README (empty package); needs Mach Zig 2026.4.10 (0.16-dev) while CI pins 0.14 with no runs. Immutable, no C ABI, arity 3 only, u32 slot math caps \~3.8B keys, fixed seed; contain() on an empty filter reads uninitialized memory.

## Caveats and trade-offs

Both sides of the comparison are this library's own Zig types (BinaryFuse vs Xor/Fuse) in the same harness. Nothing in this repo is measured against the C reference xor_singleheader, a Bloom filter or a cuckoo filter. The README's 'faster than Bloom, smaller than Cuckoo' line cites the Graf & Lemire papers, not local measurements. The published tables were made with Zig 0.12.0-dev.706. src/benchmark.zig has since been ported to newer Zig APIs, so the numbers do not come from the current code. contains() is no faster than xor; the win is build time and memory. The canonical source is now code.hexops.org (Forgejo, 0 stars). The GitHub repo hexops/fastfilter is archived (293 stars), not a redirect, and the README's build.zig.zon example still points to the GitHub archive URL.

Zig-only (not directly usable from C/C++ without a C ABI shim); iterator-based population reduces memory; larger fingerprint widths (u16/u32) trade memory for lower false-positive rate; GitHub mirror is archived, canonical repo moved to project's own Forgejo instance

## Maintenance

Maintained only through Zig-version bumps: the last algorithm fix was v0.10.2, the changelog stops at v0.11.0, and the last commit (April 2026) moved to Zig 2026.4.10-mach. It lives on a self-hosted Forgejo with no issues, PRs or CI runs, next to an archived GitHub mirror with issues disabled. It is dual MIT/Apache-2.0 and about 70 KB of dependency-free Zig, so vendoring src/ is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks section runs binaryfuse against xor (and fuse) filters in one public harness, src/benchmark.zig. It states the compiler (Zig 0.12.0-dev.706+62a0fbdae), the flags (-O ReleaseFast) and the CPUs (AMD Ryzen 9 3900X, and a 2.3 GHz 8-core Intel Core i9 in a 2019 MacBook Pro). That meets A, although both sides are this library's own Zig implementations.
- **Verifier notes:** Downgraded for the overstated claim, not the tier. The record's '\~19x-4x faster at 100M keys' is wrong: 28.0/7.4 is \~3.8x. 'i9-9900K-class' is also wrong, since the page gives only a 2.3 GHz 8-core i9 (a laptop part). The license (dual MIT/Apache-2.0 LICENSE files), the last commit (2026-04-11 UTC) and the GitHub mirror's 293 stars check out.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/README.md>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter/commits?limit=2>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/LICENSE>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/src/benchmark.zig>
  - <https://github.com/hexops/fastfilter>
- **Sources the enricher read:**
  - <https://code.hexops.org/hexops/fastfilter>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/README.md>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter/git/trees/main?recursive=true>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter/commits?limit=15>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter/issues?state=all&type=issues>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter/pulls?state=all>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter/actions/tasks>
  - <https://code.hexops.org/api/v1/repos/hexops/fastfilter/tags>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/src/binaryfusefilter.zig>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/src/xorfilter.zig>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/src/main.zig>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/src/util.zig>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/src/unique.zig>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/src/benchmark.zig>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/build.zig>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/build.zig.zon>
  - <https://code.hexops.org/hexops/fastfilter/raw/branch/main/.forgejo/workflows/ci.yml>
  - <https://code.hexops.com/hexops/fastfilter>
  - <https://github.com/hexops/fastfilter>
  - <https://github.com/hexops/fastfilter/blob/main/README.md>
  - <https://machengine.org/docs/nominated-zig/>
  - <https://arxiv.org/abs/2201.01174>
  - <https://hn.algolia.com/api/v1/search?query=hexops%20fastfilter&restrictSearchableAttributes=url>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://code.hexops.org/hexops/fastfilter`) · [data/wave6/enrich/raw/code_hexops_org_hexops_fastfilter.json](../../../data/wave6/enrich/raw/code_hexops_org_hexops_fastfilter.json) (enrichment confidence 0.85)

</details>
