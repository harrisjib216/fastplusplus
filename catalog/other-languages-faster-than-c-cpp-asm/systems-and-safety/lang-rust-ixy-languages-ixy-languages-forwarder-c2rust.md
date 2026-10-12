# ixy network driver in Rust (C2Rust-transpiled unsafe build versus C)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-2-Clause` · 🔵 finished

> C2Rust-transpiled, fully unsafe Rust build of the ixy user-space 10G NIC driver; 91 vs 94 cycles per packet against C.

| | |
|---|---|
| **Beats** | ixy C user-space network driver packet forwarder (gcc, and clang with the same LLVM version) |
| **Claimed result** | Rust-vs-C-performance.md: the C2Rust-transpiled, fully unsafe Rust driver forwards a packet in 91 cycles with 121 instructions, 'faster than the original code', also when C is compiled with clang on the same LLVM version. The C rows in the same document are 94 cycles and 127 instructions at batch 32 (108 and 139 at batch 8), so about 3% fewer cycles than C at batch 32 (derived from page data; the document does not state the batch size of the C2Rust run). The idiomatic safe Rust driver is slower: 100 vs 94 cycles at batch 32 and 120 vs 108 at batch 8, executing 65% more instructions. |
| **Workload** | CPU cycles and instructions per forwarded 64-byte packet by the ixy forwarder at batch sizes 32 and 8 on an Intel 82599-class NIC, measured with CPU performance counters (paper: The Case for Writing Network Drivers in High-Level Programming Languages, ANCS 2019). |
| **Metric** | other |
| **Hardware** | Intel Xeon E3-1230 v3 per the Rust-vs-C document (the repo README names an E3-1230 v2 at 3.3 GHz for the throughput graphs) |
| **Compiler and flags** | C baseline: emmericp/ixy CMakeLists.txt compiles with -g -O2 -march=native -fomit-frame-pointer (current HEAD; the file was last changed in November 2019). ixy.rs Cargo.toml sets no profile overrides (cargo release default opt-level 3, no target-cpu). Compiler versions and the C2Rust build's flags are not stated. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Document reports fewer executed instructions per packet in the transpiled build (121 vs 127) but gives no deeper mechanism; for safe Rust it explains that out-of-order CPUs hide bounds-check overhead (IPC 2.09 vs 1.35). |
| **Adoption** | 2.2k stars |
| **Last commit** | 2022-12-14 |
| **Links** | [repository](https://github.com/ixy-languages/ixy-languages) · [benchmark](https://raw.githubusercontent.com/ixy-languages/ixy-languages/HEAD/Rust-vs-C-performance.md) |

## Verdict

With perf stat counters on a Xeon E3-1230 v3 forwarding 64-byte packets between two ixgbe ports, C ixy (gcc 6.3, -O2 -march=native) used 94 cycles and 127 instructions per packet at batch 32 (108 and 139 at batch 8); the C2Rust transpilation used 91 cycles and 121 instructions (batch size not stated) and was reported faster than a clang build on the same LLVM as well. The idiomatic safe ixy.rs used 100 and 120 cycles (209 and 232 instructions) at batch 32 and 8.

## Use it when

- Evidence when planning a C-to-Rust migration with C2Rust: the transpiled, unsafe stage of a packet-processing hot path need not be slower than the original C on the same LLVM.
- Studying the cost of Rust safety in a driver: the same document quantifies bounds checks (6% more cycles at batch 32, 11% at batch 8) and integer overflow checks (0.8% throughput at batch 8).
- Learning user-space NIC drivers on Linux x86-64 with an ixgbe-family card or virtio, using the published C driver or ixy.rs (about 1000 to 2000 lines each).
- Reproducing per-packet counter methodology: perf stat with the ocperf wrapper on a forwarder under full bidirectional 64-byte load (issue #6).

## Skip it when

- As a library or driver to deploy: the C2Rust build is unpublished, and ixy.rs itself says it is not production-ready and that DMA may corrupt memory.
- As proof that Rust codegen beats C: the gain is 3 cycles per packet (about 3%, derived) from one unreplicated run, with no variance, batch size, compiler versions or flags given.
- Where you need safety: the faster variant is wholly unsafe transpiled code; the safe idiomatic driver is 6-11% slower in cycles per packet.
- Non-Intel or non-x86 NICs and hosts: only ixgbe-family devices and virtio are supported, and the drivers need hugepages plus root or an IOMMU with vfio-pci.

## How it is fast

C2Rust turns the C into unsafe Rust that keeps raw pointers and has almost no bounds checks, so the hot loops match the C logic; the document reports 121 instead of 127 instructions per packet and gives no further mechanism. One plausible, untested source of those 6 instructions: the C build compiles ixgbe.c, memory.c and ixy-fwd.c separately with no -flto, so pkt_buf_alloc (called per received packet) and pkt_buf_free (per sent packet) are out-of-line cross-file calls, whereas rustc optimises a whole crate and can inline across its modules. The safe ixy.rs driver is a different story: it executes about 65% more instructions (bounds checks, wrapper objects) that the out-of-order core mostly hides (IPC 2.09 vs 1.35).

## Compared with alternatives

Unlike libbzip2-rs or fast_rsync, which ship Rust code you can link and measure against a C library, this is a measurement without an artefact; use it only as a data point that transpiled unsafe Rust can match C in a hot I/O path, and take the published ixy.rs if you need a working safe driver.

## Integration

| | |
|---|---|
| **Form** | not published (transpiled driver); the related ixy.rs is a Cargo crate and ixy C is a CMake project |
| **Dependencies** | ixy.rs: libc, byteorder, log, lazy_static; ixy C: none beyond libc and Linux sysfs/vfio |
| **Minimum toolchain** | not documented for the C2Rust build; ixy.rs uses edition 2018; the main counter table used gcc 6.3 for C and roughly Rust 1.36 nightly (issue #6) |
| **Platforms** | Linux x86-64 with an Intel 82599/X520, X540 or X550 NIC (ixgbe, ixgbevf in ixy.rs) or virtio; hugepages required |
| **Thread safety** | not documented for the C2Rust build; the forwarder is single-threaded and the README recommends one process per RSS queue instead of shared threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness gaps: the C2Rust claim is two sentences added on 2019-10-30, after the ANCS 2019 paper (whose abstract, seen as a search snippet, reports only the safe driver: 63% more instructions, 4% slower); the transpiled source, rustc and clang versions, flags, batch size and number of runs are not given, and the clang comparison's own cycle count is not stated.
- Baseline build: ixy C is compiled with -g -O2 -march=native -fomit-frame-pointer and no -flto (unchanged since the 2017 initial import), while Rust optimises a whole crate at opt-level 3; the maintainer reports -O3 was sometimes slightly slower than -O2 (issue #6), so -O2 is not a crippled baseline, but the missing LTO is an untested confound for the 6-instruction difference.
- The safe-Rust rows are not a pure bounds-check measurement: ixy.rs prefetches every received packet with _mm_prefetch (T1) in rx_batch (commit c734821, May 2019, gated on target_feature sse, which x86_64 targets have by default), while ixy C has no prefetch, which matches the table's C-only L2 and L3 hits (1.1 and 0.9 per packet at batch 32).
- Hardware differs across the repo: the counter table ran on a Xeon E3-1230 v3, the README throughput graphs on an E3-1230 v2 at 3.3 and 1.6 GHz, and the latency plots on a Xeon E5-2620 v3.

## Known shortcomings

- The 91 vs 94 cycles line was added 2019-10-30 (commit e543831) after the ANCS 2019 paper; the transpiled code and its flags are unpublished; the C baseline is -O2 -march=native; the gain is 3 cycles from a single run.
- The transpiled code is unpublished and the claim is 91 vs 94 cycles from a single run with batch size and flags unstated. Issue #6: C used gcc 6.3 -O2 (the maintainer says -O3 is sometimes slower) and Rust about 1.36 nightly. Possible untested confound: C is built without -flto, so per-packet pkt_buf_alloc and pkt_buf_free are cross-file calls, which could explain the 6 fewer instructions. Safe ixy.rs prefetches each RX packet (commit c734821) while C does not, so the safe-vs-C rows are not a pure bounds-check cost. Papers were reachable only as snippets.

## Caveats and trade-offs

The C2Rust claim is a tongue-in-cheek addendum added to the repository on 2019-10-30, after the ANCS 2019 paper; whether the paper contains it could not be checked (arXiv and net.in.tum.de blocked here). The transpiled C2Rust driver is not published in the ixy-languages organisation as far as I could find. The difference is 3 cycles per packet from one run on one Intel Xeon E3-1230 v3, with no variance reported, and the batch size of the C2Rust run is not stated. The C baseline is built at -O2 -march=native, not -O3, while Rust release builds default to opt-level 3, so optimisation levels are not matched. The document gives no mechanism beyond 6 fewer instructions per packet. Hardware differs between this document (E3-1230 v3) and the README throughput graphs (E3-1230 v2). The repository has been quiet since December 2022; the README marks each driver 'Finished'. [retier] Enricher: the claim is 91 vs 94 cycles from a single run with batch size and flags unstated. Issue #6: C used gcc 6.3 -O2 (the maintainer says -O3 is sometimes slower) and Rust about 1.36 nightly. Possible untested confound: C is built without -flto, so per-packet pkt_buf_alloc and pkt_buf_free are cross-file calls, which could explain the 6 fewer instructions. Safe ixy.rs prefetches each RX packet (commit c734821) while C does not, so the safe-vs-C rows are not a pure bounds-check cost.

Faster variant is entirely unsafe transpiled Rust without bounds checks; the safe idiomatic driver pays about 65% more instructions that out-of-order execution mostly hides.

## Maintenance

Finished: the summary repo's last change is PR #13 'typo in C2Rust name' (2022-12-14) and every driver is marked Finished, though ixy.rs still took a register-write fix on 2026-10-09; the summary repo is BSD-2-Clause and ixy.rs MIT, but the C2Rust driver behind the claim was never published, so only the C and safe Rust drivers can be reused.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The C2Rust result (91 cycles, 121 instructions per packet) is a two-sentence addendum the authors added to Rust-vs-C-performance.md on 2019-10-30 (commit e543831, 'rust can be faster than C :)'), after the ANCS 2019 paper; the transpiled code, compiler versions and flags are not published, so it is first-party numbers without methodology (C), not peer-reviewed (B).
- **Verifier notes:** Numbers are on the page but the 'Rust is faster than C' line rests on a 3-cycle difference from unpublished transpiled code, added after the paper; tier C. The C baseline is -O2 (emmericp/ixy CMakeLists.txt), so it misses the wave's -O3 rule; record shortcomings: unmatched opt levels, no published C2Rust code, no flags or versions, single run, within-noise gain.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ixy-languages/ixy-languages/HEAD/Rust-vs-C-performance.md>
  - <https://raw.githubusercontent.com/ixy-languages/ixy-languages/HEAD/README.md>
  - <https://github.com/ixy-languages/ixy-languages>
  - <https://github.com/ixy-languages/ixy-languages/commits/master>
  - <https://github.com/ixy-languages/ixy-languages/commits/master/Rust-vs-C-performance.md>
  - <https://github.com/ixy-languages/ixy-languages/commit/e543831c2b75d085665bb3ed6771abe46533ff45>
  - <https://raw.githubusercontent.com/emmericp/ixy/HEAD/CMakeLists.txt>
  - <https://github.com/emmericp/ixy/commits/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ixy-languages/ixy.rs/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ixy-languages/ixy-languages/HEAD/Rust-vs-C-performance.md>
  - <https://raw.githubusercontent.com/ixy-languages/ixy-languages/HEAD/README.md>
  - <https://github.com/ixy-languages/ixy-languages>
  - <https://github.com/orgs/ixy-languages/repositories>
  - <https://github.com/ixy-languages/ixy-languages/tree/master/slides>
  - <https://github.com/ixy-languages/ixy-languages/commit/e543831c2b75d085665bb3ed6771abe46533ff45>
  - <https://github.com/ixy-languages/ixy-languages/issues?q=is%3Aissue>
  - <https://github.com/ixy-languages/ixy-languages/issues/6>
  - <https://github.com/ixy-languages/ixy-languages/issues/12>
  - <https://github.com/ixy-languages/ixy-languages/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/ixy-languages/ixy.rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/ixy-languages/ixy.rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ixy-languages/ixy.rs/HEAD/examples/forwarder.rs>
  - <https://raw.githubusercontent.com/ixy-languages/ixy.rs/HEAD/src/ixgbe.rs>
  - <https://raw.githubusercontent.com/ixy-languages/ixy.rs/HEAD/src/memory.rs>
  - <https://github.com/ixy-languages/ixy.rs/commits/master>
  - <https://github.com/ixy-languages/ixy.rs/commits/master/src/memory.rs>
  - <https://raw.githubusercontent.com/emmericp/ixy/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/emmericp/ixy/69e9d8d/CMakeLists.txt>
  - <https://raw.githubusercontent.com/emmericp/ixy/cfdeb91/CMakeLists.txt>
  - <https://github.com/emmericp/ixy/commits/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/emmericp/ixy/HEAD/src/app/ixy-fwd.c>
  - <https://raw.githubusercontent.com/emmericp/ixy/HEAD/src/driver/ixgbe.c>
  - <https://raw.githubusercontent.com/emmericp/ixy/HEAD/src/driver/device.h>
  - <https://raw.githubusercontent.com/emmericp/ixy/HEAD/src/memory.c>
  - WebSearch snippets for the ANCS 2019 paper (arXiv 1909.06344) and for ixy C2Rust; www.net.in.tum.de paper PDF (proxy 403) and mediatum.ub.tum.de (ENOTFOUND) blocked
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/ixy-languages/ixy-languages#forwarder-c2rust`) · [data/wave14/enrich/raw/lang_rust_ixy_languages_ixy_languages_forwarder_c2rust.json](../../../data/wave14/enrich/raw/lang_rust_ixy_languages_ixy_languages_forwarder_c2rust.json) (enrichment confidence 0.55)

</details>
