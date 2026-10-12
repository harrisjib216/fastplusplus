# LLVM lld (LLVM linker)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Linkers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> LLVM's drop-in linker (ELF, COFF, Mach-O, Wasm): roughly 2x to 12x faster than GNU ld and gold, though mold and wild now beat it.

| | |
|---|---|
| **Beats** | GNU gold and GNU ld |
| **Claimed result** | Independent (Wild benchmark page, AMD Ryzen 9 9955HX, GNU ld 2.46 vs LLD 21.1.8, chart labels relative to Wild 0.10.0): lld links ripgrep 4.9x, wild-debug 7.0x, mold-gdb-index 12.1x and rust-hello-world 2.0x faster than GNU ld, with near parity on c-hello-world (1.06x) and linker-plugin LTO wild-lto (1.12x) (all derived from page data). First-party lld docs table (lld/docs/index.md, about 2017, 2-socket 20-core Xeon E5-2680 2.80 GHz with SSD), lld w/threads vs GNU gold w/threads: ffmpeg dbg 0.35s vs 1.01s, mysqld dbg 0.68s vs 2.68s, clang dbg 5.28s vs 23.49s, chromium dbg 16.70s vs 60.82s; GNU ld took 1.72s, 8.50s, 104.03s and 209.05s on the same four programs. Docs text: 'you can expect that LLD runs more than twice as fast as the GNU gold linker' on a large program on a multicore machine. |
| **Workload** | Link time of four large debug-info programs (ffmpeg, mysqld, clang, chromium) with GNU ld, GNU gold and lld, each with and without multi-threading. |
| **Metric** | build-time |
| **Hardware** | Independent run: AMD Ryzen 9 9955HX 16-core/32-thread, 92 GiB RAM, output on tmpfs. lld docs table: 2-socket 20-core 40-thread Xeon E5-2680 2.80 GHz with an SSD drive |
| **Adoption** | llvm-project 41k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/llvm/llvm-project) · [benchmark](https://github.com/davidlattimore/wild/blob/main/benchmarks/ryzen-9955hx.md) |

## Verdict

Independent benchmark (Wild project, AMD Ryzen 9 9955HX 16C/32T, 92 GiB RAM, output on tmpfs, Ubuntu packages GNU ld 2.46 and LLD 21.1.8, ten batches of eight runs per linker): lld linked ripgrep in about 92 ms vs 451 ms for GNU ld, wild-debug in 215 ms vs 1512 ms and mold-gdb-index in 790 ms vs 9.7 s, with near parity on c-hello-world (19.6 vs 20.7 ms) and LTO (11.4 vs 12.8 s). The ratios are derived from the chart labels; there are no gold rows. The lld docs' own roughly 2017 table, on a 2-socket 20-core Xeon E5-2680, shows threaded lld 2.9x to 4.4x faster than threaded gold and 4.9x to 19.7x faster than GNU ld on ffmpeg, mysqld, clang and chromium debug links.

## Use it when

- Replacing GNU ld (BFD) for large C, C++ or Rust ELF links. On a Ryzen 9 9955HX, lld 21.1.8 linked ripgrep 4.9x, wild-debug 7.0x and mold-gdb-index 12.1x faster than GNU ld 2.46 (derived from page data).
- Replacing GNU gold, which binutils 2.44 (Feb 2025) deprecated and moved out of the default tarball. lld also beat gold 2.9x to 4.4x on threaded debug links in its own 2017 table.
- Toolchains that already ship lld. rustc uses rust-lld by default on x86_64-unknown-linux-gnu since 1.90.0, where the Rust team measured 7x faster linking for an incremental ripgrep debug rebuild.
- Cross-compiling or targeting several object formats with one linker: ELF for AArch64, ARM, LoongArch, PPC/PPC64, RISC-V, x86 and x86-64 at 'production quality', plus PE/COFF with PDB debug info, Mach-O and WebAssembly.
- Clang LTO and ThinLTO without a linker plugin, since bitcode is read natively; or embedding the linker in a tool through lld::lldMain.

## Skip it when

- When link time on ELF is the bottleneck and mold or wild can link your program. On Wild's page lld is 6.2s vs 2.06s for mold and 0.99s for wild on chrome, and 7.7s vs 3.6s and 2.5s on clang-debug. mold's August 2026 table has lld 3.8x to 16.1x slower than mold on a Threadripper 7980X.
- Expecting gains from many-core machines: unless --threads= is given, lld caps itself at 16 threads. Its own commit a8788de1 reports that more than 16 threads made links slower, so extra cores do not help it.
- Tiny links or linker-plugin LTO, where gains mostly vanish: c-hello-world was 1.06x faster than GNU ld, and in wild-lto lld (11.4s) is within 8% of GNU ld, mold and wild because LLVM code generation dominates.
- Builds that depend on GNU ld's exact archive-order semantics or on undocumented linker-script corner cases. Rust's announcement warns that lld 'is not bug-for-bug compatible with GNU ld', and ELF/linker_script.md lists intentional deviations.
- Small-memory build machines when moving from GNU ld: on ripgrep lld's peak RSS was 177 MiB vs 95 MiB for GNU ld (read from Wild's chart). On the big links it uses less memory than mold, for example 9.1 GiB vs 9.5 GiB on chrome.

## How it is fast

The design document (NewLLD.md) puts it as doing less work: section contents and relocations are not read until they are needed, and each symbol name is hashed into the symbol table only once. After that the linker works through Symbol pointers that resolution replaces in place, using placement new. Archives are handled the Windows way: lld remembers every archive symbol it has seen, so it never rescans archives or loops over --start-group. Input loading, post-parse, ICF, the sharded string merging in MergeNoTailSection (32 shards keyed by high hash bits), .gdb_index construction and output writing all run on LLVM's parallelFor. The 2017 docs table shows most of the gain comes from doing less work rather than from threads: single-threaded lld beats single-threaded gold 1.9x to 2.8x, and 40 threads add only 1.7x to 2.8x more.

## Compared with alternatives

Pick lld over mold or wild when you need something they lack: PE/COFF with PDB, Mach-O or WebAssembly output, built-in LTO, an embeddable library, or a linker that rustc and Clang toolchains already ship. Pick mold or wild for raw ELF link speed, where both are several times faster on large debug links. On Mach-O, zld competes only with Apple's ld64; lld's Mach-O port claims more than 2x over ld64, but no numbers were read for that.

## Integration

| | |
|---|---|
| **Form** | Built from the llvm-project monorepo. Ships as a CLI binary (lld, with symlinks ld.lld, lld-link, ld64.lld and wasm-ld) and as static driver libraries (lldELF, lldCOFF, lldMachO, lldWasm, lldMinGW) for embedding through lld::lldMain. |
| **Dependencies** | LLVM core libraries from the same tree (Support, Object, LTO and the target backends); CMake &gt;= 3.20 and Python &gt;= 3.8 to build; zlib or zstd optional for compressed debug sections. |
| **Minimum toolchain** | C++17 (LLVM_REQUIRED_CXX_STANDARD 17); host compiler Clang 5.0, Apple Clang 10.0, GCC 7.4 or Visual Studio 2019 16.8 or newer. |
| **Platforms** | Runs wherever LLVM builds: Linux, BSDs, macOS, Windows. Targets ELF (AArch64, ARM &gt;= v4, LoongArch, PowerPC, PowerPC64, RISC-V, x86-32 and x86-64 at production quality; MIPS 'decent'; also AMDGPU, Hexagon and SPARC V9), PE/COFF (complete, including PDB), Mach-O and WebAssembly, listed by the docs in descending order of completeness. |
| **Thread safety** | As a CLI it is internally multithreaded via LLVM's parallel strategy (capped at 16 threads unless --threads=N; --threads=1 disables threading). As a library, Driver.h describes lldMain as 'safe for re-entry' with crash recovery, and its canRunAgain flag reports whether another call is safe. Running several links concurrently in one process is not documented. Open issue #66974: exitLld called from a worker thread races in llvm_shutdown. |
| **Drop-in for the baseline** | partial — it accepts GNU ld/gold command lines and linker scripts and is selected with -fuse-ld=lld, but archive resolution differs on purpose: --start-group is redundant, and a link can succeed under lld that fails under GNU ld or pick a different archive member. Linker-script behaviour also deviates in documented corner cases. |

## Gotchas

- Undocumented thread cap: Driver.cpp limits lld to 16 threads when --threads= is not given, but the --threads help text in Options.td still says 'By default all available hardware threads are used'. Every third-party comparison run at default options (Wild's runner passes no thread flag; mold's README says 'default options' on a 64-core Threadripper) measures lld at 16 threads, which its maintainers say is its best setting.
- Archive semantics: lld remembers the symbol tables of archives it has already passed, so 'ld def.a ref.o' links under lld but fails under GNU ld. When two archives define the same symbol, the two linkers can silently pick different objects. Use --warn-backrefs to find these cases before switching.
- The headline docs table cannot be rerun as written. It is first-party, from about 2017 (the same page says 'as of February 2017'), gives no command lines or inputs, and disabled threading with -no-threads, which current Options.td no longer has (the equivalent is --threads=1). Its GNU ld rows also drop -icf=all and -gdb-index, which GNU ld did not support.
- Harness note on Wild's mold-gdb-index row (12.1x over GNU ld): the runner aborts on any linker error or on output containing 'warning:', and lld's docs say GNU ld lacks --gdb-index. So GNU ld cannot have been given an unsupported --gdb-index. Either its unpublished per-linker flags dropped the option, or GNU ld built no index and did less work than lld. Either way the inputs are unpublished. If GNU ld skipped the index, the ratio understates lld's advantage rather than favouring lld, as the record's caveat suggests.

## Known shortcomings

- Upgraded C to B on the independent Wild benchmark page (davidlattimore/wild benchmarks/ryzen-9955hx.md, Ryzen 9 9955HX, GNU ld 2.46 vs LLD 21.1.8): 1.06x to 12.1x faster than GNU ld, ripgrep 4.9x (derived from page data). The \~2017 docs table is first-party. No gold rows or published inputs on the Wild page; near parity on tiny and LTO links; mold and wild are several times faster than lld.
- Enricher: all six Wild-page ratios match (4.9x, 7.0x, 12.1x, 2.0x, 1.06x, 1.12x, re-read from the SVG chart). Harness notes: the Wild runner passes no thread flag and lld/ELF/Driver.cpp caps lld at 16 threads unless --threads= is given (Options.td help text still says all hardware threads), so Wild (32-thread CPU) and the mold README (64-core Threadripper, default options) both measure lld at 16 threads; commit a8788de1 says more than 16 threads is slower for lld, so the cap is lld's own best setting. The runner aborts on any linker error or 'warning:' output, so GNU ld cannot have run with unsupported --gdb-index in the mold-gdb-index row; the 12.1x figure more likely understates lld than favours it. The \~2017 docs table is first-party and its -no-threads flag is gone (now --threads=1), so it is not rerunnable as written. lld peak RSS 177 MiB vs 95 MiB for GNU ld on ripgrep; gold deprecated in binutils 2.44; archive semantics differ from GNU ld (--warn-backrefs); open issue #66974 (exitLld race when embedded); mold and wild are several times faster on ELF.

## Caveats and trade-offs

The lld docs table is first-party, undated but from about 2017 (the same page says 'as of February 2017'; the file was rewritten to Markdown on 2026-07-16 without changing the table); the four programs, link command lines, compiler and flags are not given. GNU ld rows drop -icf=all and -gdb-index because GNU ld lacks them (footnote says GNU ld would be slower with them). The docs warn results vary with cores, memory and disk. The independent Wild benchmark covers GNU ld (BFD) only in a few charts and has no GNU gold rows; its captured inputs are not published, the ratios are derived from chart percentage labels relative to Wild 0.10.0, and the mold-gdb-index case may favour lld if GNU ld lacks --gdb-index. Gains shrink to near parity on tiny programs (c-hello-world 1.06x) and with linker-plugin LTO (wild-lto 1.12x). Newer linkers are much faster than lld: on the same Wild page lld is +519% vs Wild 0.10.0 on chrome and +207% on clang-debug, and mold's README (August 2026, Threadripper 7980X, inputs on Zenodo) reports mold 4.9x faster than lld at the median (mold's author is lld's original developer). llvm-project is already in the catalog (AddressSanitizer entry), hence the paper:llvm-lld-linker id. The 'LLVM' list entry is a collection; lld is the component with the clearest numeric comparison found. A numeric Clang-vs-GCC compile-time comparison was not found on a reachable page (blog.llvm.org blocked). [retier] Wild page (Ryzen 9 9955HX, GNU ld 2.46 vs LLD 21.1.8) runs lld at its default 16-thread cap (lld/ELF/Driver.cpp; its own best setting per commit a8788de1). The mold-gdb-index row's 12.1x more likely understates lld (runner aborts on unsupported flags, so GNU ld ran without --gdb-index or with unpublished per-linker flags). No gold rows or published inputs; near parity on tiny and LTO links; mold and wild several times faster. First-party \~2017 docs table not rerunnable (-no-threads flag removed). lld peak RSS 177 MiB vs 95 MiB GNU ld on ripgrep; archive semantics differ (--warn-backrefs); open #66974 exitLld race when embedded.

Drop-in replacement for GNU linkers (same command line and linker scripts); ELF, PE/COFF, Mach-O and WebAssembly ports of differing completeness; LTO supported by default; some very old Unix linker features removed.

## Maintenance

Very active: the lld directory had commits from October 2 to October 6, 2026. Apache-2.0 WITH LLVM-exception, already packaged by every major distro, and the default linker for rustc on x86-64 Linux, so it is usable today. Three caveats on the evidence: Wild's chart inputs and per-linker flags are unpublished, the docs table is first-party and about nine years old, and lld's speed edge over GNU linkers is now well behind mold and wild on ELF.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: besides the first-party lld docs table (stated hardware, no programs, command lines or harness, so C on its own), the independent Wild linker project's benchmark page (benchmarks/ryzen-9955hx.md, AMD Ryzen 9 9955HX 16-core, 92 GiB RAM, output on tmpfs, 99% confidence intervals) times GNU ld 2.46 and LLD 21.1.8 (Ubuntu packages) on the same inputs and shows lld 1.06x to 12x faster. Not A because the captured link inputs and the build flags of the linked programs are not published there.
- **Verifier notes:** lld docs numbers match the record exactly; I upgraded C to B on Wild's independent GNU ld 2.46 vs LLD 21.1.8 benchmark and moved benchmark_url there, keeping the docs table in claimed_speedup (the docs URL is https://github.com/llvm/llvm-project/blob/main/lld/docs/index.md). Metadata checked: llvm-project about 41k stars, Apache-2.0 WITH LLVM-exception (LICENSE.TXT), not archived; last_commit 2026-10-06 not re-checked but plausible. Shortcomings to record: docs table is 2017-era first-party without command lines, independent page lacks gold and published inputs, near parity on small or LTO links, mold and wild are several times faster than lld.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 2); enricher (wave 2)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/index.md>
  - <https://github.com/llvm/llvm-project>
  - <https://github.com/llvm/llvm-project/commits/main/lld/docs/index.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/LICENSE.TXT>
  - <https://github.com/davidlattimore/wild/blob/main/benchmarks/ryzen-9955hx.md>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/ryzen-9955hx.md>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/README.md>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/ripgrep-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/wild-debug-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/mold-gdb-index-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/chrome-time.svg>
  - <https://raw.githubusercontent.com/rui314/mold/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/index.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/README.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/NewLLD.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/ELF/warn_backrefs.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/ELF/linker_script.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/MachO/index.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/windows_support.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/docs/ReleaseNotes.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/include/lld/Common/Driver.h>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/ELF/Driver.cpp>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/ELF/SyntheticSections.cpp>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/ELF/SyntheticSections.h>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/ELF/Writer.cpp>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/ELF/ICF.cpp>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/lld/ELF/Options.td>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/llvm/docs/GettingStarted.md>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/llvm/CMakeLists.txt>
  - <https://github.com/llvm/llvm-project/commits/main/lld>
  - <https://github.com/llvm/llvm-project/commit/a8788de1c3f3c8c3a591bd3aae2acee1b43b229a>
  - <https://github.com/llvm/llvm-project/issues?q=is%3Aissue+is%3Aopen+label%3Alld%3AELF+label%3Aperformance>
  - <https://github.com/llvm/llvm-project/issues?q=is%3Aissue+label%3Alld%3AELF+slow>
  - <https://github.com/llvm/llvm-project/issues/66974>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/ryzen-9955hx.md>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/ryzen-9955hx.toml>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/runner/src/main.rs>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/runner/src/benchmarking.rs>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/runner/src/config.rs>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/runner/Cargo.toml>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/ripgrep-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/wild-debug-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/mold-gdb-index-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/rust-hello-world-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/c-hello-world-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/wild-lto-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/chrome-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/clang-debug-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/clang-release-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/wild-time.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/chrome-memory.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/clang-debug-memory.svg>
  - <https://raw.githubusercontent.com/davidlattimore/wild/HEAD/benchmarks/images/ryzen-9955hx/ripgrep-memory.svg>
  - <https://raw.githubusercontent.com/rui314/mold/HEAD/README.md>
  - <https://github.com/rust-lang/blog.rust-lang.org/pull/1682/files>
  - <https://raw.githubusercontent.com/rust-lang/blog.rust-lang.org/main/content/rust-lld-on-stable-1.90.0/index.md>
  - WebSearch: binutils 2.44 gold deprecation (LWN, Fedora wiki and LLVM Discourse snippets; pages not opened)
  - WebSearch: lld 16-thread cap commit (snippet led to the commit page above)
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `paper:llvm-lld-linker`) · [data/wave2/enrich/raw/paper_llvm_lld_linker.json](../../../data/wave2/enrich/raw/paper_llvm_lld_linker.json) (enrichment confidence 0.85)

</details>
