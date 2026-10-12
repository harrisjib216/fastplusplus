# Wild (wild-linker)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Linkers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust linker for Linux that beats LLVM lld on debug-build link time via mmap'd input and rayon-parallelized phases.

| | |
|---|---|
| **Beats** | lld |
| **Claimed result** | In mold's README benchmark table (linkers built 2026-08-28, median of 3 runs), wild links faster than lld on every row where wild can link (7 programs per table x 4 tables = 28 rows). Examples on the Threadripper 7980X, debug builds: Blender 4.72s(lld)-&gt;1.98s(wild)=2.4x, ClickHouse 6.62s-&gt;4.40s=1.5x, Godot 1.77s-&gt;1.08s=1.6x, Chromium 16.64s-&gt;3.98s=4.2x. Across the 28 supported rows, lld/wild runs from 1.38x to 4.18x, median \~2.1x (derived from page data). The same page shows wild slower than mold (mold claims 1.9x faster than wild at the median). wild's own BENCHMARKING.md hyperfine output (ripgrep: wild 10.88x faster than GNU ld, 1.67x faster than mold) is explicitly an illustrative example ('with different values'), not a reported result. |
| **Workload** | mold README benchmark: 9 programs (Blender 5.2, Chromium 145, Clang 21, ClickHouse 26.1, Firefox 149, Godot 4.6, LibreOffice 26.2, PyTorch 2.9, TensorFlow 2.21, plus ARM64 builds of Chromium and Firefox) linked in debug and release configurations on an AMD Ryzen Threadripper 7980X and an Apple M1 Ultra (perf cores only). Times are wall-clock medians of 3 runs after a warm-up. Per the page, wild's N/A rows mean wild cannot link that program (TensorFlow, Firefox debug, ARM64 Chromium/Firefox). Chromium release rows are N/A for a different reason: wild does not implement --icf=all. |
| **Metric** | build-time |
| **Hardware** | AMD Ryzen Threadripper 7980X (64 cores), Ubuntu 24.04; Apple M1 Ultra (16P+4E cores, perf cores only), Fedora Asahi Remix 42 (per mold's benchmark table) |
| **Compiler and flags** | All three linkers (lld, wild, mold) were built from source in release configuration as of 2026-08-28 and run with their default options. The toolchain/compiler versions used to build the linkers are not stated. |
| **Adoption** | 3.99k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/wild-linker/wild) · [benchmark](https://github.com/rui314/mold#benchmark) |

## Verdict

Verified against mold's own August 2026 README benchmark table (all three linkers built from source in release mode as of 2026-08-28, wall-clock median of 3 runs after warm-up, on a Threadripper 7980X/Ubuntu 24.04 and an M1 Ultra/Fedora Asahi 42): wild beat lld on all 28 rows where it could link (per-row ratios 1.38x-4.18x, median \~2.1x, e.g. Chromium debug 16.64s to 3.98s), while mold beat wild on those same rows by \~1.9x at the median.

## Use it when

- Iterative Linux debug builds (Rust/Cargo, or C/C++ via Clang or GCC 16.1+/CMake 4.4+) where lld's link time is the edit-compile-link bottleneck, for a program wild can link (Blender, Clang, ClickHouse, Godot, LibreOffice, PyTorch, Chromium debug all measured 1.4x-4.2x faster than lld).
- Projects already invoking lld via -fuse-ld=lld/--ld-path=lld — swapping to wild is a flag-value change, no build-system rework.
- x86-64, ARM64, riscv64gc, PPC64LE, or LoongArch64 Linux targets, especially with Clang or GCC 16.1+ / CMake 4.4+ for first-class integration.
- Teams that want an actively developed, Rust-native alternative to mold specifically because mold's author has ruled out incremental linking.
- Experimental wasm32-wasip1/wasm32-unknown-unknown linking, if you're comfortable with a feature flagged as experimental (--features wasm).

## Skip it when

- Release builds needing --icf=all (identical code folding) — wild doesn't implement it, so it is N/A on the mold benchmark's Chromium-release rows rather than just losing some size savings.
- Programs wild can't link at all yet: TensorFlow 2.21, Firefox debug builds, and ARM64 Chromium/Firefox are N/A for wild in the mold benchmark suite.
- Any Mach-O (Apple) or Windows target, or non-Linux host — unsupported.
- Builds depending on fuller linker-script features (SEARCH_DIR, STARTUP, TARGET, INSERT, NOCROSSREFS, REGION_ALIAS, MEMORY '&gt;region' placement, PHDRS AT attribute) — only partially implemented per LINKER_SCRIPT_SUPPORT.md.
- When mold is an option and Rust-native tooling isn't a requirement: mold links the same benchmark suite \~1.9x faster than wild at the median and covers more architectures (adds i386, PowerPC, s390x, LoongArch32, SPARC64, m68k, SH-4).

## How it is fast

Wild mmaps input files instead of read()-ing them, deduplicates merge-string sections up front, and resolves symbols through a hashmap before touching relocations — the same input-handling strategy mold uses. Its phases (symbol_db, resolution, layout, elf_writer) run on a rayon-owned thread pool, using par_iter/par_bridge to parallelize the relocation-graph traversal and the copy/relocate step in the ELF writer, with only a few phases left single-threaded. It isn't algorithmically different from mold — both are mmap-plus-parallel-ELF-writer designs — it is simply slower in practice today (mold's README puts wild \~1.9x behind mold at the median on the same benchmark).

## Compared with alternatives

Pick wild over lld whenever your debug-link target is in its supported set — it's 1.4x-4.2x faster with an identical invocation. Pick mold instead of wild when you just want the fastest available Linux linker today (mold beats wild by \~1.9x at the median on the same benchmark) and don't specifically need Rust-native tooling or wild's incremental-linking roadmap; zld isn't a real alternative here since it only targets Apple's ld64, not ELF.

## Integration

| | |
|---|---|
| **Form** | crate (cargo-installed binary) — invoked as your linker executable, not linked into your program |
| **Dependencies** | none to vendor as a unit; Rust workspace of 7 crates pulling \~40 crates.io deps, notably rayon (thread pool), hashbrown/foldhash (symbol hashmap), gimli (DWARF), iced-x86, blake3, zlib-rs, clap |
| **Minimum toolchain** | Rust 1.97.1 (workspace rust-version), edition 2024, to build wild itself; to use it as your linker you need Clang or GCC 16.1+ for -fuse-ld=wild, or CMake 4.4+ for CMAKE_LINKER_TYPE=WILD |
| **Platforms** | Linux only — x86-64, ARM64, RISC-V (riscv64gc), LoongArch64 and PPC64LE (both 'initial support'); WebAssembly output experimental behind --features wasm; no Mach-O, no Windows |
| **Thread safety** | not documented as an embeddable library — it's a CLI tool; internally uses a rayon-owned thread pool across most phases (par_iter/par_bridge), with a few phases intentionally single-threaded per DESIGN.md |
| **Drop-in for the baseline** | partial — same invocation surface as lld (-fuse-ld=wild, --ld-path=wild, -B&lt;dir&gt; trick, CMAKE_LINKER_TYPE=WILD) but not feature-complete: no --icf=all, partial linker-script support, and it cannot link every program lld can (TensorFlow, Firefox debug, ARM64 Chromium/Firefox in the mold benchmark) |

## Gotchas

- GCC before 16.1 rejects -fuse-ld=wild outright; use the ld.wild symlink plus -B/tmp workaround documented in the README.
- Archive entry load order and symbol-resolution priority don't yet fully match GNU ld/LLD semantics (open issue #600), which can change which duplicate symbol wins in ambiguous builds.
- wild's Chromium-release 'N/A' in the mold benchmark is a deliberate limitation (no --icf=all), not a crash — don't assume every N/A row is a bug.
- The repo was transferred from davidlattimore/wild to the wild-linker org; the old URL redirects, but pin CI/install scripts to the new path.

## Caveats and trade-offs

The primary benchmark is in the README of a rival project (mold, whose author competes with wild). That page shows wild beating lld on every supported row but losing to mold on most rows. wild cannot link several programs in the suite (TensorFlow, Firefox debug, ARM64 Chromium/Firefox) and lacks --icf=all. wild also publishes its own benchmarks: benchmarks/ryzen-9955hx.md (AMD Ryzen 9 9955HX, runner code in benchmarks/runner, config in ryzen-9955hx.toml) compares against LLD 21.1.8, mold and GNU ld, but its numbers exist only as SVG charts (e.g. the clang-release chart labels LLD 21.1.8 as +400% vs Wild 0.10.0). BENCHMARKING.md shows only example output. The repository was transferred from davidlattimore/wild to the wild-linker org, and the old URL redirects. GitHub reports the license as Apache-2.0 only, but the README and the LICENSE-APACHE/LICENSE-MIT files confirm a dual license.

No incremental linking yet (the stated long-term goal of the project, unimplemented); does not support --icf=all, so cannot correctly replace lld/mold for ICF-enabled release builds (e.g. Chromium); Linux/ELF-focused, with experimental/limited WebAssembly support; fewer target platforms than mold or lld.

## Maintenance

Actively maintained (3,998 stars, commits the same day as this record, not archived or a fork) and permissively dual-licensed (Apache-2.0 OR MIT confirmed in-repo, though GitHub's UI reports only Apache-2.0); still pre-1.0 (v0.10.0) with incremental linking — the project's actual reason for existing — not yet built.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B-&gt;A. mold README benchmark gives lld vs wild vs mold wall-clock times, and the machines are named (Threadripper 7980X / Ubuntu 24.04, M1 Ultra / Fedora Asahi 42). It also gives the build/benchmark configuration (all linkers built from source in release configuration as of 2026-08-28, default options, median of 3 runs after warm-up), and the benchmark code is public: the Zenodo record 21882261 (bench.tar.gz) includes the build and evaluation scripts plus all linker inputs. Tier rules say who ran it does not matter, so the rival-README cap to B does not apply.
- **Verifier notes:** Numbers verified against the mold README table; the record's claim that wild is faster on 'most rows' is corrected to 'every supported row'. The record's workload wrongly said TensorFlow/Firefox N/A was due to missing ICF: the page says those are programs wild cannot link. Metadata matches (3,998 stars, last commit 2026-09-24, not archived, not a fork). The record said wild had no numbers of its own; that is wrong, since wild's in-repo benchmarks/ directory has them.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rui314/mold#benchmark>
  - <https://zenodo.org/records/21882261>
  - <https://github.com/wild-linker/wild>
  - <https://github.com/davidlattimore/wild>
  - <https://github.com/wild-linker/wild/blob/main/BENCHMARKING.md>
  - <https://github.com/wild-linker/wild/blob/main/benchmarks/ryzen-9955hx.md>
  - <https://github.com/wild-linker/wild/blob/main/benchmarks/ryzen-9955hx.toml>
  - <https://github.com/wild-linker/wild/blob/main/benchmarks/images/ryzen-9955hx/clang-release-time.svg>
- **Sources the enricher read:**
  - <https://github.com/wild-linker/wild>
  - <https://github.com/wild-linker/wild/blob/main/README.md>
  - <https://github.com/wild-linker/wild/blob/main/Cargo.toml>
  - <https://github.com/wild-linker/wild/blob/main/DESIGN.md>
  - <https://github.com/wild-linker/wild/blob/main/LINKER_SCRIPT_SUPPORT.md>
  - <https://github.com/wild-linker/wild/blob/main/LICENSE-APACHE>
  - <https://github.com/wild-linker/wild/blob/main/LICENSE-MIT>
  - <https://github.com/wild-linker/wild/issues/600>
  - <https://github.com/rui314/mold#benchmark>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/wild-linker/wild`) · [data/wave2/enrich/raw/github_com_wild_linker_wild.json](../../../data/wave2/enrich/raw/github_com_wild_linker_wild.json) (enrichment confidence 0.85)

</details>
