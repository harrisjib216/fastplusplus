# rav1d-safe

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Rust` · `AGPL-3.0-only OR LicenseRef-Imazen-Commercial (Cargo.toml, LICENSE-AGPL3, LICENSE-COMMERCIAL); code inherited from dav1d/rav1d is BSD-2-Clause (COPYING)` · 🟢 active

> Memory-safe Rust AV1 decoder (rav1d fork); faster only than upstream rav1d with its assembly disabled, slower than dav1d.

| | |
|---|---|
| **Beats** | upstream memorysafety/rav1d commit d3d1cd6 (package 1.1.0) built with default-features=false (bitdepth_8, bitdepth_16 only), i.e. with its hand-written assembly disabled; not dav1d and not rav1d's default assembly build, both of which are faster |
| **Claimed result** | Against upstream rav1d without assembly only: checked rav1d-safe takes 0.680x the time with 1 worker (32.0% less decode time), 0.821x with 4 workers and 0.813x with 8 workers (geometric mean of 12 still inputs); for example photo-8k-min 1 worker 231.372 ms vs 451.903 ms (0.512x), while map inputs are 0.755-1.002x. Against assembly-enabled upstream rav1d it is slower: a separate 2026-09-07 page (different inputs: a 720x300 24-frame video, a 1024x1024 still, a 256x256 10-bit still; older rav1d-safe revision d1767a1) shows checked rav1d-safe taking 1.77-8.62 times as long with one frame in flight and up to 12.8x against upstream frame threading, and the README's historical v0.5.6 table shows 1.56x (4K) and 1.54x (8K) the ASM build's time on AVIF stills. |
| **Workload** | Still-image AV1 decode (12 inputs: photo and map at 1920x1080, 3840x2160, 7680x4320, minimum tiling and eight tiles, 8-bit 4:2:0 IVF) with 1, 4 and 8 workers; median of five paired repetitions per cell, geometric mean across inputs, MD5-checked against upstream and dav1d 1.5.3. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7900X (24 logical CPUs) |
| **Compiler and flags** | Rust 1.98.1 (LLVM 22.1.8), release, fat LTO, one codegen unit, unwind panics, RUSTFLAGS=-C llvm-args=-align-all-functions=4; upstream rav1d commit d3d1cd6 with default-features=false (bitdepth_8, bitdepth_16); rav1d-safe commit be5b244 checked features (no unchecked, c-ffi, asm) |
| **Adoption** | 9 stars, 3 forks, 1,460 commits; crates.io rav1d-safe 0.6.0 published 2026-09-08, 15,003 total downloads |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/imazen/rav1d-safe) · [benchmark](https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/noasm-2026-09-08/README.md) |

## Verdict

On an AMD Ryzen 9 7900X with Rust 1.98.1 (LLVM 22.1.8), fat LTO, one codegen unit and identical RUSTFLAGS for both arms, checked rav1d-safe (commit be5b244, staged 0.6.0 with a git-pinned archmage, not the crates.io package that depends on archmage ^0.9.29) decoded 12 single-frame 8-bit 4:2:0 IVF stills in 0.680x (1 worker), 0.821x (4) and 0.813x (8) the time of upstream rav1d d3d1cd6 built with default-features=false. The stills are photo and map at 2K/4K/8K, each with minimum and eight tiles. Figures are geometric means of medians of five paired repetitions, and every run was MD5-checked against upstream and dav1d 1.5.3. The baseline is a non-default scalar build, and compare.py's rotate-then-reverse ordering cancels out for two arms, so upstream always ran first in each pair (the page discloses the fixed order).

## Use it when

- Decoding untrusted AVIF/AV1 stills in a Rust server where a forbid(unsafe_code) decoder with no assembly is a hard requirement
- As a replacement for upstream rav1d built without assembly (for example, a target or policy that rules out nasm/asm): on 2K-8K photo stills it took 0.51-0.78x the time, and on map stills 0.755-1.002x
- Tiled stills decoded with tile threading (1/4/8 workers, max_frame_delay=1), which works in the default checked build
- Verifying AV1 encoder output: the default Strictness::Strict reports desynchronised symbol streams as errors where dav1d would conceal them
- Cargo-only builds that still need SIMD on x86-64 (AVX2/AVX-512) and aarch64 (NEON)

## Skip it when

- When throughput is what matters: dav1d and default (assembly) rav1d are faster. The author's 2026-10-01 profile puts the default build at 1.72-1.74x dav1d 1.5.3's time on 4K stills, and the 2026-09-07 grid at 1.8-8.6x upstream's time (up to 12.8x against upstream frame threading)
- Inter-heavy video playback: on a 480p inter stream the default build took 2.68 ms/frame against dav1d's 0.83, mostly in warp motion compensation, and frame threading in 0.6.0 needs the unchecked feature
- Closed-source products without buying Imazen's commercial licence: the crate is AGPL-3.0-only OR LicenseRef-Imazen-Commercial (the code inherited from dav1d/rav1d is BSD-2-Clause)
- Pre-AVX2 x86 (no SSE tier, so it falls back to scalar) or ARM cores where dav1d's SVE2/dotprod/i8mm paths matter (only baseline NEON is ported)
- Streams that need S-frames, SVC operating-point selection or the argon vectors: 19 of 803 dav1d-test-data vectors are not exercised

## How it is fast

Against upstream's no-assembly build, the speed comes from having SIMD at all. rav1d-safe ports dav1d's x86 and ARM assembly families to safe Rust SIMD: motion compensation, inverse transforms, intra prediction, CDEF, loop filter, loop restoration, film grain, palette and refmvs, plus an inlined msac entropy decoder. It uses archmage capability-token dispatch (AVX2, some AVX-512, NEON) and safe_unaligned_simd loads. Upstream rav1d with default-features=false falls back to its scalar Rust code. Runtime DisjointMut overlap tracking stays on in the default build; on 4K AVIF it costs about 3.9 of 42.4 ms per frame against dav1d 1.5.3 (docs/SAFE_VS_DAV1D.md).

## Compared with alternatives

Pick dav1d (catalogued, BSD-2-Clause, beats libaom) whenever speed or permissive licensing matters. Pick rav1d-safe only when a Rust decoder with no assembly and forbid(unsafe_code) is required. rusty-av1-toolkit is catalogued for its rav1e encoder speed; its rav1d-derived decoder has no catalogued decoder benchmark.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | archmage, safe_unaligned_simd, rav1d-disjoint-mut, enough, whereat, parking_lot, zerocopy, strum, atomig, bitflags, raw-cpuid, aligned and small helpers; build dependencies cc and nasm-rs (assembly is used only by the opt-in asm/partial_asm modes); libc only with c-ffi |
| **Minimum toolchain** | Rust 1.89 (edition 2024); the AVIF test and benchmark tooling needs Rust 1.93 |
| **Platforms** | x86-64 (AVX2 and partial AVX-512 SIMD; scalar below AVX2), aarch64 (NEON); i686, armv7 and riscv64gc listed as supported targets |
| **Thread safety** | Internal tile-thread pool set by Settings.threads; Frame is Arc-backed and cloneable; Send/Sync for Decoder not documented |
| **Drop-in for the baseline** | partial — the native Rust API differs from upstream rav1d's Decoder/Picture API (decode(&[u8]) vs send_data/get_picture); the c-ffi/dav1d-compat features export dav1d_\* C symbols but disable forbid(unsafe_code) |

## Gotchas

- Strictness::Strict is the default and rejects non-conforming streams that dav1d conceals; set Strictness::Lenient for dav1d-identical behaviour on corrupt input
- Feature names moved after 0.6.0: the published crate's unchecked feature (frame threading, no overlap tracking) is called untracked on main, which also adds frame threading to tracked builds. The README table still says unchecked
- Published 0.6.0 returns wrong mastering-display values (wrong fixed-point units; a 1000-nit maximum reads as 25.6 nits). The fix is only on main (Unreleased)
- frame_size_limit defaults to 120 megapixels and bounds only declared dimensions, not decode time; use set_stop for cancellation on untrusted input

## Known shortcomings

- The win is only against upstream rav1d d3d1cd6 built without assembly; against dav1d or rav1d with assembly it is slower. The 1.77-8.62x figures come from a separate 2026-09-07 page with different inputs and an older revision (up to 12.8x against frame threading). Licence is AGPL-3.0-only or commercial, plus BSD-2-Clause inherited code; crates.io 0.6.0 is published. Usability mixed.
- The timed be5b244 used a git-pinned archmage while crates.io 0.6.0 uses archmage ^0.9.29; compare.py's rotate-then-reverse cancels for two arms with upstream always first (disclosed). 0.6.0's mastering-display metadata is wrong (1000 nit reads as 25.6), fixed only on main; unchecked was renamed untracked after 0.6.0. The 2026-10-01 docs put the default build at 1.72-1.74x dav1d 1.5.3's time on 4K stills (480p inter 2.68 vs 0.83 ms), so it stays slower than dav1d with assembly.

## Caveats and trade-offs

Not faster than the incumbent: against dav1d or assembly-enabled rav1d it is 1.5-8.6x slower on the author's own pages (1.54-1.56x on 4K/8K AVIF stills at v0.5.6; 1.77-8.62x on the 2026-09-07 video/still grid, up to 12.8x against upstream frame threading, which the checked fork cannot use yet). The only win is against upstream rav1d with its assembly turned off (which still contains unsafe Rust), on a 12-input still-image seed corpus (photo and map at 2K/4K/8K, minimum and eight tiles); map cells are near parity (0.755-1.002x) and the page says this is not a SIMD ablation and does not establish parity with the assembly default. Fixed A/B arm order may bias results. The 1.8-8.6x figures come from a separate page with different inputs and an older rav1d-safe revision, not the same page set. Dual AGPL-3.0/commercial licensing (copyleft; commercial key required for closed-source use) limits reuse. The baseline is not in the FFmpeg, x264, Opus list.

Memory-safe AV1 decoder: replaces about 160,000 lines of assembly with checked safe Rust SIMD under forbid(unsafe_code), native Rust API (C API behind an optional c-ffi feature that implies unchecked). Strict mode by default rejects non-conforming streams that dav1d conceals. Fork of rav1d, which is a port of dav1d.

## Maintenance

Very active (commits on 2026-10-01; 0.6.0 published 2026-09-08 with about 15k total downloads; 451 closed issues, none open), but AGPL-3.0-only or a paid commercial licence and a speed deficit against dav1d make it a memory-safety pick, not a speed upgrade.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks/noasm-2026-09-08/README.md gives Rust 1.98.1 (LLVM 22.1.8), release/fat LTO/one codegen unit/RUSTFLAGS -C llvm-args=-align-all-functions=4, AMD Ryzen 9 7900X, pinned commits, and the public harness benchmarks/noasm-2026-09-08/reproduce.py with benchmarks/stills-2026-09-07/compare.py and benchmarks/upstream-2026-09-07/driver/src/main.rs (MD5-validated against upstream and dav1d 1.5.3); all numbers in the record appear there, but the A applies only to the no-assembly upstream baseline.
- **Verifier notes:** Tier A stands for the no-assembly comparison (public reproduce.py, compiler, flags, CPU, MD5 checks). Usability left as mixed: the licences are OSI (AGPL-3.0-only, BSD-2-Clause for inherited code) but copyleft/commercial dual licensing plus a win only against a non-default upstream build make it a memory-safety pick, not a speed pick. Fixed 'same page set' wording, crate status (0.6.0 is published, not staged) and licence string.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `license`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/noasm-2026-09-08/README.md>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/noasm-2026-09-08/reproduce.py>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/noasm-2026-09-08/EVIDENCE.json>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/upstream-2026-09-07/README.md>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/upstream-2026-09-07/driver/src/main.rs>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/stills-2026-09-07/compare.py>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/LICENSE-COMMERCIAL>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/COPYING>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/rav1d-safe>
  - <https://github.com/imazen/rav1d-safe>
  - <https://github.com/imazen/rav1d-safe/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/noasm-2026-09-08/README.md>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/noasm-2026-09-08/reproduce.py>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/noasm-2026-09-08/EVIDENCE.json>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/upstream-2026-09-07/README.md>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/upstream-2026-09-07/driver/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/upstream-2026-09-07/driver/src/main.rs>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/stills-2026-09-07/compare.py>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/tracker-sharding-2026-09-07/build.py>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/tracker-sharding-2026-09-07/drivers/current/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/benchmarks/tracker-sharding-2026-09-07/drivers/current/main.rs>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/release/0.6.0/feature-renames.json>
  - <https://raw.githubusercontent.com/imazen/rav1d-safe/HEAD/docs/SAFE_VS_DAV1D.md>
  - <https://crates.io/api/v1/crates/rav1d-safe>
  - <https://crates.io/api/v1/crates/rav1d-safe/0.6.0>
  - <https://crates.io/api/v1/crates/rav1d-safe/0.6.0/dependencies>
  - <https://github.com/imazen/rav1d-safe>
  - <https://github.com/imazen/rav1d-safe/commits/main>
  - <https://github.com/imazen/rav1d-safe/issues>
  - <https://github.com/imazen/rav1d-safe/issues?q=is%3Aissue%20state%3Aclosed>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/imazen/rav1d-safe`) · [data/wave10/enrich/raw/github_com_imazen_rav1d_safe.json](../../../data/wave10/enrich/raw/github_com_imazen_rav1d_safe.json) (enrichment confidence 0.75)

</details>
