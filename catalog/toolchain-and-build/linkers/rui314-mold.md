# mold

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Linkers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Drop-in ELF linker beating LLVM lld and GNU ld via pervasive data-parallelism across the whole link pipeline.

| | |
|---|---|
| **Beats** | lld |
| **Claimed result** | 4.9x faster than LLVM lld and 1.9x faster than wild at the median (August 2026 benchmark); per-program lld/mold ratios in the published table range from \~1.5x up to 16.1x depending on program/build-type/machine (e.g. TensorFlow debug on Threadripper: 50.73s (lld) -&gt; 3.15s (mold) = 16.1x; Blender release on M1 Ultra: 0.56s (lld) -&gt; 0.25s (mold) = 2.3x) |
| **Workload** | Linking 9 large real-world programs (Blender, Chromium, Clang, ClickHouse, Firefox, Godot, LibreOffice, PyTorch, TensorFlow, some also in ARM64 variants) in both debug and release configurations, on an AMD Ryzen Threadripper 7980X (Ubuntu 24.04) and an Apple M1 Ultra (Fedora Asahi Remix 42); wall-clock time, median of 3 runs after a warm-up run. |
| **Metric** | build-time |
| **Hardware** | AMD Ryzen Threadripper 7980X (64 cores), Ubuntu 24.04; Apple M1 Ultra (16 performance + 4 efficiency cores, benchmark restricted to performance cores), Fedora Asahi Remix 42 |
| **Compiler and flags** | All three linkers (lld, wild, mold) built from source 'in release configuration' as of 2026-08-28 and run with default options; exact compiler/version and flags used to compile the 9 benchmarked programs themselves are not enumerated in the README, only that debug vs. release build variants were both tested. |
| **Adoption** | 17.2k stars; default linker for many large open-source projects, in production use since 2021 (author is the original developer of LLVM lld) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/rui314/mold) · [benchmark](https://github.com/rui314/mold#benchmark) |

## Verdict

On 9 real-world programs (Blender, Chromium, Clang, ClickHouse, Firefox, Godot, LibreOffice, PyTorch, TensorFlow, some ARM64 variants) linked in both debug and release configurations, mold beat LLVM lld by 4.9x at the median (per-program range \~1.5x-16.1x) and wild by 1.9x at the median. All three linkers were built from source in release mode as of 2026-08-28 with default options; measurements are wall-clock, median of 3 runs after a warm-up, on an AMD Ryzen Threadripper 7980X/Ubuntu 24.04 and an Apple M1 Ultra/Fedora Asahi Remix 42.

## Use it when

- Large C/C++/Rust ELF builds on Linux/Unix where the link step dominates the debug-edit-rebuild loop — mold shows 4x-16x over lld on multi-GB debug binaries (per-program table in README).
- Many-core workstations or CI runners (Threadripper-class) where lld/gold leave most cores idle during linking.
- Toolchains that already select a linker via `-fuse-ld=`/`-B` (Clang, GCC 12.1+, Rust via `.cargo/config.toml`) — swapping in mold is a one-line config change.
- Any of the 16 listed non-Windows/non-macOS ELF targets, including cross-linking ARM64 output from an x86 host.
- Teams that want bit-for-bit deterministic link output with no host-specific default paths baked in.

## Skip it when

- Native Windows/MSVC or macOS/Mach-O link jobs: the mold.exe binary builds and runs on Windows, but per the maintainer (issue #1658) it 'can only be used to link ELF binaries' — no PE/COFF or Mach-O support, and macOS support was explicitly ruled out (issue #1052 thread).
- Projects relying on non-trivial linker-script features (custom SECTIONS/memory layouts, embedded/microcontroller link maps) — mold supports only the minimal subset needed to parse glibc's loader script and has stated no plan to add more (open issue #243, 'SECTIONS doesn't seem to be implemented').
- Workloads needing incremental or partial linking (gold-style `--incremental`, or `-r` combined with LTO) — not supported; every invocation is a full relink.
- Small link jobs on few-core machines: on the M1 Ultra debug table mold actually regressed vs. lld for Clang (0.9x) — the parallel design needs enough cores/input size to pay for itself.
- If you need long field-history on the exact codebase in production: the linker rewrote from C++ to Rust just before this snapshot (Sept 2026, issue #1655), so 'production since 2021' applies to the predecessor C++ implementation, not the current Rust one.

## How it is fast

Per the ASPLOS 2027 paper ('mold: A Massively Parallel Linker'), mold decouples the traditionally entangled passes of Unix linking — symbol resolution, archive-member pulling, relocation, output layout — so each stage is split across a rayon-based work-stealing thread pool (capped at 32 threads by default) instead of running mostly single-threaded like lld/gold. Section-merging deduplication uses a custom lock-free, open-addressing concurrent hash map (CAS-claimed buckets, per-shard probing) whose table size is pre-estimated with HyperLogLog cardinality counting rather than grown/resized on the fly. The paper's ablation study found no single optimization dominates — the speedup is cumulative across nearly every pass being parallelized.

## Compared with alternatives

Pick mold over wild when you need broader architecture coverage (16 ISAs vs. wild's more limited set) or maximum throughput on many-core Linux boxes: mold is \~1.9x faster than wild at the median, and wild is marked N/A (can't link at all) on several rows in mold's own table, including Chromium release builds because it lacks --icf=all. mold and zld don't really compete — zld targets Apple's ld64/Mach-O toolchain exclusively, so on macOS zld is the only option of the two; mold has explicitly ruled out macOS support.

## Integration

| | |
|---|---|
| **Form** | crate (Cargo workspace building a CLI binary `mold` + companion shared object `mold-wrapper.so`; not a library you link against) |
| **Dependencies** | Rust crates: rayon, hashbrown, memmap2, blake3, xxhash-rust, crc32fast, zstd, flate2, libz-sys, cpp_demangle, rustc-demangle, bstr, memchr, getrandom, libc. Build also needs a C compiler (GCC/Clang) and Git. |
| **Minimum toolchain** | Rust stable toolchain (Cargo.toml workspace edition 2024, i.e. rustc 1.85+); rust-toolchain.toml pins channel "stable". |
| **Platforms** | Linux/Unix ELF targets: x86-64, i386, ARM32/64 (+BE), RISC-V32/64 (+BE), PowerPC32/64 (v1/v2), s390x, LoongArch32/64, SPARC64, m68k, SH-4. Also builds on Windows (CI job build-windows.ps1 produces mold.exe) but, per the maintainer, can then only link ELF output, not PE/COFF. |
| **Thread safety** | Not documented as a library API (mold is CLI-only, no embeddable interface). Internally rayon-driven; thread count defaults to min(cores,32) and is configurable via --thread-count/--no-threads. Output is documented as deterministic/bit-for-bit reproducible regardless of thread scheduling. |
| **Drop-in for the baseline** | partial — CLI-compatible drop-in via -fuse-ld=mold/-B (same invocation mechanism and most flags as GNU ld/lld for ordinary builds), but only a minimal linker-script subset is implemented, so builds relying on custom scripts (SECTIONS etc.) will not work. |

## Gotchas

- --start-group/--end-group are accepted for compatibility but silently ignored — mold (like lld) tracks archive symbols globally so link order doesn't matter, which can surprise anyone relying on that flag's traditional semantics.
- No incremental or partial (-r + LTO) linking; every run is a full relink.
- Only a minimal linker-script subset is supported (just enough to read glibc's ASCII libc.so loader script); no plans to extend it.
- Windows builds of the CLI exist but only link ELF, not PE/COFF — don't expect an MSVC linker replacement.

## Caveats and trade-offs

The README numbers are self-reported by the mold maintainer. However, the Zenodo artifact (https://zenodo.org/records/21882261, the ASPLOS 2027 paper artifact, mixed licenses, 27GB bench.tar.gz) includes the build/evaluation scripts, container image, and linker inputs. Hardware, OS, date, and run method are stated. The exact compiler and flags used to build the 9 test programs are not listed in the README. The README tables compare only lld and wild. The companion paper 'mold: A Massively Parallel Linker' (ASPLOS 2027, arXiv 2608.23228) reports '2.4-16.1x faster than ... lld' and 'up to 112x faster than the traditional GNU ld'. mold is now written in Rust (built with Cargo).

As of the current main branch mold has been rewritten from C++ to Rust (confirmed via repo language metadata, README build instructions requiring Cargo, and the author's own Sept 2026 announcement); no incremental linking; supports x86-64/i386/ARM32/64/RISC-V32/64/PowerPC32/64/s390x/LoongArch32/64/SPARC64/m68k/SH-4 but has no native Windows/MSVC target; on the M1 Ultra debug-build table, mold is actually slower than lld for Clang (0.9x, i.e. a regression on that one workload).

## Maintenance

Actively maintained (last commit 2026-09-23; 140+ contributors; CI test-builds \~19,000 Gentoo packages against GNU ld as a control before each release); MIT-licensed with prebuilt binaries via most distro package managers and GitHub releases, though the linker core is a very recent (Sept 2026) full rewrite from C++ to Rust.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The README benchmark tables compare lld, wild, and mold on 9 programs on a Threadripper 7980X and an M1 Ultra. They state the build configuration (release builds of all linkers as of 2026-08-28, default options, median of 3 after warm-up). The public Zenodo artifact (records/21882261) contains the mold linker, build/evaluation scripts, a container image, and all linker inputs. The artifact belongs to a peer-reviewed ASPLOS 2027 paper.
- **Verifier notes:** Every number in claimed_speedup matches the README tables: 4.9x/1.9x median, 50.73s to 3.15s = 16.1x, 0.56s to 0.25s = 2.3x, and a 1.5x minimum (Clang 21 debug, M1 Ultra). The paper provides a GNU ld comparison that the README lacks. Metadata verified: MIT, 17239 stars, last commit 2026-09-23, primary language Rust.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rui314/mold#benchmark>
  - <https://github.com/rui314/mold>
  - <https://zenodo.org/records/21882261>
  - <https://arxiv.org/abs/2608.23228>
- **Sources the enricher read:**
  - <https://github.com/rui314/mold>
  - <https://github.com/rui314/mold#benchmark>
  - <https://github.com/rui314/mold/blob/main/rust-toolchain.toml>
  - <https://github.com/rui314/mold/blob/main/Cargo.toml>
  - <https://github.com/rui314/mold/blob/main/LICENSE>
  - <https://github.com/rui314/mold/blob/main/.github/workflows/build-windows.ps1>
  - <https://github.com/rui314/mold/blob/main/.github/workflows/release-assets.yml>
  - <https://github.com/rui314/mold/blob/main/docs/mold.md>
  - <https://github.com/rui314/mold/blob/main/src/util/concurrent_map.rs>
  - <https://github.com/rui314/mold/blob/main/src/util/hyperloglog.rs>
  - <https://github.com/rui314/mold/issues/1052>
  - <https://github.com/rui314/mold/issues/1591>
  - <https://github.com/rui314/mold/issues/1658>
  - <https://arxiv.org/abs/2608.23228>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/rui314/mold`) · [data/wave2/enrich/raw/github_com_rui314_mold.json](../../../data/wave2/enrich/raw/github_com_rui314_mold.json) (enrichment confidence 0.92)

</details>
