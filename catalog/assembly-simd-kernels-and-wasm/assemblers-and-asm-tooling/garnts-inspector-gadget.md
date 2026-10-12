# inspector-gadget

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `GPL-3.0` · 🟡 stale

> Multi-architecture ROP gadget finder in Rust; much faster than the Python tool Ropper on large binaries.

| | |
|---|---|
| **Beats** | Ropper (Python ROP gadget finder) |
| **Claimed result** | README: 'less than 10 seconds' (real 0m9.758s) for libmonochrome_64.so versus Ropper 'about 35 minutes'; xul.dll 'about a minute and a half' (real 1m25.907s) while Ropper was abandoned 'after about 3 hours'. About 215x and more than 125x (derived from page data). |
| **Workload** | Finding every gadget in an Android arm64 libmonochrome.so (Chrome and WebView library) and in a Windows x86_64 xul.dll, timed with `time`; disassembly via Capstone. |
| **Metric** | throughput |
| **Hardware** | 'my test box' (not stated) |
| **Compiler and flags** | target/release cargo build; Ropper and Capstone versions not stated |
| **Adoption** | 17 stars; 1.4k crates.io downloads |
| **Last commit** | 2024-05-01 |
| **Links** | [repository](https://github.com/GarntS/inspector-gadget) · [benchmark](https://github.com/GarntS/inspector-gadget) |

## Verdict

On the author's unspecified 'test box' (no CPU, Capstone or Ropper version given), a single `time` run found all gadgets in an Android arm64 libmonochrome.so in 9.758 s versus Ropper's estimated \~35 min (about 215x), and in a Windows x86_64 xul.dll in 1m25.907s while Ropper was abandoned after \~3 hours (lower bound &gt;125x). Both ratios are derived from page data; the Ropper side has no measured time and, per the README, Ropper did not de-duplicate or sort, so inspector-gadget does strictly more work, which strengthens the comparison rather than inflating it.

## Use it when

- Enumerating gadgets in very large binaries (browser engines, OS kernels, shared libraries tens to hundreds of MB) where a Python finder takes tens of minutes to hours.
- Cross-architecture work: one tool for arm64, x86_64, mips, ppc, riscv, sparc64 and s390x, with architecture and endianness auto-detected from the object headers.
- Pipelines that want de-duplicated output with all load addresses per gadget, pre-filtered by a Rust regex before writing.
- Workflows that would otherwise dump all gadgets to a file and grep it (the author's own recommendation), on machines with many cores to feed rayon.

## Skip it when

- When you need gadget semantics, chain building, or a constraint/JOP solver: this only finds and prints gadgets (ret-terminated by default; call/jmp are opt-in flags), with no chaining or search over gadget effects.
- Permissive or proprietary projects: GPL-3.0.
- When you need a validated speed figure: the published numbers are single untimed-hardware runs and the Ropper baseline is an estimate ('about 35 minutes', 'gave up after about 3 hours'), so treat the ratios as order-of-magnitude only.
- Very small binaries where either tool finishes in well under a second and the parallel setup buys nothing.
- If you need resilience to malformed input: the binary parse and segment/section reads use unwrap()/expect() throughout, so a file object cannot parse aborts the run with a panic rather than an error.

## How it is fast

The gadget search is embarrassingly parallel over a precomputed list of valid instruction start addresses (every byte on x86, every 4 bytes on fixed-width ISAs, every 2 bytes on RISC-V/s390x), fanned out with rayon; each worker thread holds its own Capstone handle in thread-local storage. A two-pass design does the bulk work without ever materialising mnemonic strings: the first pass stores only raw instruction bytes, de-duplicates them into a reversed-instruction tree (a trie rooted at each terminating instruction), and only the unique survivors are disassembled a second time to produce text, which the README says cuts both time and memory versus storing strings up front. The 100x+ gap over Ropper is mostly Rust and multithreading against a single-threaded Python tool.

## Compared with alternatives

This is the only ROP gadget finder in the category; the disassembler siblings (iced, Zydis, Fadec, bddisasm, yaxpeax-x86, diStorm3) are decode-throughput libraries, not gadget search tools. Reach for inspector-gadget when the task is finding gadgets across many architectures fast; reach for one of those decoders when you are building your own analysis on raw instruction streams.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | capstone 0.12 and capstone-sys 0.16 (link the Capstone engine), object 0.35 for file parsing, rayon 1.10, regex 1.10, clap 4.5, indicatif 0.17, itertools 0.12 |
| **Minimum toolchain** | Rust 2021 edition; a C toolchain to build the bundled Capstone via capstone-sys |
| **Platforms** | Host tool for any platform Rust+Capstone build on; the target binary may be any of the 12 supported ISAs regardless of host |
| **Thread safety** | Single-process CLI; internally multithreaded with rayon, one Capstone handle per thread in TLS |
| **Drop-in for the baseline** | partial — a faster alternative to Ropper's gadget-finding, but a different CLI and output format, and it omits Ropper's chain-building and semantic features |

## Gotchas

- `cargo install inspector-gadget` builds capstone-sys from source, so a C compiler and the usual native-build setup are needed; the only published crate version is 0.3.0.
- Output is a gadget mnemonic plus its list of addresses, not a ready chain; de-duplication means a gadget appears once with many addresses rather than once per address.
- Terminating-instruction detection is hand-written per architecture (RISC-V and s390x match raw ret opcodes, s390x reg-operand counting drops to the capstone-sys C API); on RISC/CISC targets without clean Capstone call/jmp group tags the README warns the call/jmp options are 'less effective or non-functional'.
- Relies on Capstone for all decoding, so it inherits Capstone's decode coverage and any decode bugs for a given ISA version (Capstone and Ropper versions behind the numbers are not stated).

## Known shortcomings

- Ropper timings are anecdotal or lower bounds from single runs with no hardware stated; Ropper skipped dedup and sort, so it did not do extra work; loose fit for the assemblers category (binary tooling).
- Enricher: anecdotal baseline (a single time run against Ropper's 'about 35 min' and 'gave up after about 3 hours'; the roughly 215x and over 125x are derived); Ropper did less work (no dedup or sort), so the comparison is not inflated; Rust plus rayon plus Capstone with a two-pass disassembly and a reversed-instruction dedup trie; GPL-3.0; unwrap/expect everywhere, panics on bad input; last commit 2024-05-01.

## Caveats and trade-offs

Single timed run per binary with `time` on an unspecified 'test box'; the README's own TODO says 'collect better data and make some graphs'. The Ropper side has no timing output: libmonochrome is 'about 35 minutes', and for xul.dll the author gave up after about 3 hours ('anecdotally it used to be a run it overnight sort of problem'), so only a lower bound exists. Per the README, Ropper's run did not de-duplicate or sort the gadgets, so inspector-gadget does at least that extra work; Ropper, Capstone and inspector-gadget versions and the gadget-length settings used for Ropper are not stated. Test binaries (libmonochrome_64.so, xul.dll) are not in the repo. Ratios of about 215x and more than 125x are derived from page data. ROP-gadget search is binary-analysis tooling, so the category fit is loose and Ropper is not in the category's baseline list. GPL-3.0 (copyleft).

GPL-3.0. Depends on Capstone for decoding; covers arm, arm64, x86, x86_64, mips, mips64, ppc, ppc64, riscv, riscv64, sparc64 and s390x with PE/COFF, ELF and Mach-O parsing. De-duplicates and sorts gadgets (Ropper did not, per the README).

## Maintenance

Stale: 20 commits, all 17 April to 1 May 2024, no issues or GitHub releases, one crates.io version 0.3.0 (1,425 downloads); GPL-3.0, usable as published via cargo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README timings (real 0m9.758s for libmonochrome_64.so, real 1m25.907s for xul.dll) against Ropper figures given only as 'about 35 minutes' and 'gave up after about 3 hours'; no CPU model, no versions, no benchmark script, test binaries not published.
- **Verifier notes:** Numbers match the README Performance section exactly; the record's caveat that Ropper does extra work was backwards (README says Ropper skipped de-duplication and sorting), corrected. Metadata verified: GPL-3.0, 17 stars, 1 fork, 20 commits, last commit 2024-05-01 (stale), crates.io 1,425 downloads, single version 0.3.0. Shortcomings: anecdotal baseline timings, single runs, unstated hardware, loose category fit.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-46 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/README.md>
  - <https://github.com/GarntS/inspector-gadget>
  - <https://github.com/GarntS/inspector-gadget/commits>
  - <https://crates.io/api/v1/crates/inspector-gadget>
- **Sources the enricher read:**
  - <https://github.com/GarntS/inspector-gadget>
  - <https://github.com/GarntS/inspector-gadget/commits>
  - <https://github.com/GarntS/inspector-gadget/tree/main/src>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/README.md>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/src/disasm_tools.rs>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/src/gadget_tree.rs>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/src/cli_args.rs>
  - <https://raw.githubusercontent.com/GarntS/inspector-gadget/HEAD/src/arch.rs>
  - <https://crates.io/api/v1/crates/inspector-gadget>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/garnts/inspector-gadget`) · [data/wave13/enrich/raw/github_com_garnts_inspector_gadget.json](../../../data/wave13/enrich/raw/github_com_garnts_inspector_gadget.json) (enrichment confidence 0.6)

</details>
