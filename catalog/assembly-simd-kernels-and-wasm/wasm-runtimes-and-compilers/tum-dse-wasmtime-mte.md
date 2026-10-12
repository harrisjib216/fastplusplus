# Cage (wasmtime-mte, MTE-based memory safety and bounds checking for 64-bit Wasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly runtimes and compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Research fork of Wasmtime 16 that swaps wasm64 software bounds checks for Arm MTE tag checks and adds MTE/PAC memory safety.

| | |
|---|---|
| **Beats** | Plain 64-bit Wasm (wasm64/memory64) run in Wasmtime without MTE, where the sandbox relies on software bounds checks; the paper reports speedups 'over wasm64' (search snippet of arXiv 2408.11456; whether the baseline build is upstream Wasmtime or the fork with MTE off was not confirmed). |
| **Claimed result** | cage-meta README abstract: memory-safety runtime overhead &lt;5.8% and memory overhead &lt;5.3% (the BibTeX abstract on the same page says &lt;3.7%), and MTE-based sandboxing 'achieving a speedup of over 5.1%'. Search snippet of arXiv 2408.11456 (snippet only): on a Google Pixel 8 (Tensor G3), PolyBench/C mean speedup of MTE sandboxing over wasm64 of 3.7±6.5%, 5.1±4.0% and 33.9±2.4% on the three core types (33.9% on the in-order Cortex-A510 cores); memory safety plus MTE sandboxing 2.1±5.6%, 4.5±4.1% and 29.2±2.5% versus wasm64. |
| **Workload** | PolyBench/C kernels compiled to 64-bit Wasm with Cage's LLVM fork and run in the wasmtime-mte fork on a Google Pixel 8 (per search snippets of the paper); Cage offloads the wasm64 sandbox bounds check to Arm MTE and adds MTE heap/stack safety and PAC pointer protection. |
| **Metric** | throughput |
| **Hardware** | Google Pixel 8 (Google Tensor G3) with Arm MTE and PAC, per the paper's artifact appendix as quoted in a search snippet; LLVM, wasmtime and benchmarks cross-compiled on an x86 host. Not confirmed from an opened page. |
| **Compiler and flags** | LLVM fork (TUM-DSE/llvm-memsafe-wasm) and wasi-libc fork; flags not stated on the pages opened |
| **Adoption** | 1 star (wasmtime-mte), 2 stars (cage-meta) |
| **Last commit** | 2026-01-14 |
| **Links** | [repository](https://github.com/TUM-DSE/wasmtime-mte) · [benchmark](https://raw.githubusercontent.com/TUM-DSE/cage-meta/HEAD/README.md) |

## Verdict

The CGO 2025 abstract (reproduced in the cage-meta README) claims MTE-based sandboxing speeds up Wasm 'by over 5.1%' at under 5.8% runtime overhead for full memory safety. An arXiv 2408.11456 search snippet (paper not reachable here) puts this as PolyBench/C on a Google Pixel 8 (Tensor G3) against wasm64 with software bounds checks in Wasmtime: 3.7±6.5%, 5.1±4.0% and 33.9±2.4% faster on the three core types (33.9% on the in-order Cortex-A510), and 2.1±5.6%, 4.5±4.1% and 29.2±2.5% with memory safety on as well. Compiler flags and harness were not inspectable.

## Use it when

- Research or prototyping of 64-bit (memory64) Wasm on Arm CPUs with MTE, such as the Google Pixel 8 (Tensor G3) used in the paper.
- Small in-order cores like Cortex-A510, where the paper snippet reports about 34% over software-checked wasm64; on bigger cores the reported gain is single digits.
- You want hardware-assisted spatial and temporal heap and stack safety for unmodified C/C++ compiled to Wasm and can adopt the authors' LLVM and wasi-libc forks.
- Reproducing or extending the CGO 2025 Cage results, where this fork is the reference runtime.

## Skip it when

- Production or multi-tenant sandboxing: it is a 1-star research fork pinned to Wasmtime 16 with no upstream security fixes since November 2023, and its tag scheme (see gotchas) is weaker than the checks it removes.
- 32-bit Wasm modules: upstream Wasmtime already removes bounds checks there with guard-page reservations, so MTE has nothing to win.
- Any CPU or kernel without MTE (all x86-64, Arm cores without the extension): the MTE options fail with 'cannot enable mte on os ..., arch ...' and you are left with plain Wasmtime 16.
- Big out-of-order cores where the reported mean gain (3.7% with a 6.5% spread on one core type) is within noise.
- Workloads that depend on Wasmtime's copy-on-write memory images for fast instantiation; they are disabled when MTE is on.

## How it is fast

Wasmtime cannot rely on guard pages for 64-bit memories, so every wasm64 load and store gets an explicit index-plus-offset compare against the bound. With mte_bounds_checks, Cranelift's bounds_checks.rs drops the compare and returns base + index + offset directly. The runtime maps linear memory with PROT_MTE, tags it in 16-byte granules with stg, and hands out a base pointer carrying tag 1 (RUNTIME_MEM_TAG). An access that lands on memory with a different allocation tag raises a synchronous tag-check fault instead of passing a software check, and guard sizes default to 0. Memory safety tags heap and stack objects with irg/stg; a prctl include mask of 0x5555 keeps those random tags even, so bit 0 stays reserved for the sandbox tag.

## Compared with alternatives

The catalogued siblings (DTVM lazy JIT, wasman and KinoWASM interpreters, WasmKit, VectorVisor on GPUs) beat other runtimes on startup, interpretation speed or GPU throughput on ordinary hardware. Pick Cage only when you specifically need wasm64 on MTE-capable Arm with hardware memory safety; for plain speed, upstream Wasmtime with 32-bit modules and guard pages already avoids the checks Cage removes.

## Integration

| | |
|---|---|
| **Form** | built from source (Rust workspace fork of the wasmtime CLI and crates) |
| **Dependencies** | TUM-DSE/wasm-tools-mte (pinned git rev 0a5ce697) for parsing; for memory safety and PAC also the LLVM fork TUM-DSE/llvm-memsafe-wasm and the wasi-libc fork martin-fink/wasi-libc |
| **Minimum toolchain** | Rust nightly per flake.nix (Cargo rust-version 1.72.0); the MTE code paths compile only with target_feature mte enabled on aarch64 |
| **Platforms** | aarch64 Linux or Android with MTE hardware and kernel PROT_MTE support (Pixel 8 in the paper); elsewhere it builds as ordinary Wasmtime 16 without the MTE features |
| **Thread safety** | Inherits Wasmtime's model; the MTE tag-check mode is set with prctl, which is per thread, only on the thread that allocates or grows a memory, and multi-threaded embedding is not documented |
| **Drop-in for the baseline** | partial: same wasmtime CLI and embedding API (as of 16.0.0) for memory64 modules plus extra flags; memory safety and PAC need recompilation with the Cage LLVM fork, and newer upstream Wasmtime APIs are missing |

## Gotchas

- Sandbox strength, from reading the code: every MTE linear memory gets the same constant tag 1 (RUNTIME_MEM_TAG in crates/runtime/src/mte.rs, applied in crates/runtime/src/mmap/unix.rs), although the CGO slides (search snippet) describe a distinct tag per sandbox. With mte_bounds_checks Cranelift emits no compare at all, and only with mem_safety is tag bit 56 forced back on. A wasm64 index that reaches another instance's linear memory, or any mapping without PROT_MTE (the Linux arm64 MTE doc raises tag-check faults only on PROT_MTE ranges), is therefore not trapped; isolation reduces to a 4-bit tag match plus unmapped pages. The paper's threat model was unreachable here.
- The tag-check mode is per thread (prctl PR_SET_TAGGED_ADDR_CTRL) and is set inside memory allocation. Growing a dynamic memory turns checking off (MTEMode::None) for the memcpy, then forces Sync mode back on and copies the tags. Wasm code running on a thread that never allocated a memory may run with tag checks ignored, which is the kernel default.
- Copy-on-write memory images are disabled with MTE: grow_to bails with 'when using MTE, memory images should be disabled', and a January 2026 commit is titled 'mte: avoid cow images with mte'. Guard regions default to 0 when mte_bounds_checks is on. Commit titles such as 'Hacky fix for address_transform w/ mte' and 'Remove potentially buggy lowering', plus three open PRs from 2023 (PAC support, deterministic stack tagging), mark this as research code.
- The speedup is only against wasm64 with software bounds checks in Wasmtime, not against 32-bit Wasm with guard pages. Whether the baseline build had Cranelift's Spectre-mitigating select enabled is not stated on any page reachable here, and the benchmark harness is in the Zenodo artifact, not in this repo.

## Known shortcomings

- Win only vs wasm64 software bounds checks: 5.1 plus or minus 4.0% mean, big cores 3.7 plus or minus 6.5%, A510 33.9%; Pixel 8 and PolyBench/C details from search snippets only; paper, Zenodo artifact and slides unreachable. Licence Apache-2.0 WITH LLVM-exception.
- Sandbox-strength flaw from the code: all MTE linear memories get the same constant tag 1 (RUNTIME_MEM_TAG in crates/runtime/src/mte.rs and mmap/unix.rs) although the CGO slides describe a distinct tag per sandbox, and mte_bounds_checks drops the bounds compare entirely (bounds_checks.rs), so an out-of-bounds index reaching another instance's memory or any non-PROT_MTE mapping is not trapped; the tag-check mode is set per thread via prctl only on the allocating thread; copy-on-write memory images are disabled. The base is Wasmtime 16.0.0 (upstream merge November 2023); the numbers remain snippet-only (arXiv and themoonlight DNS blocked).

## Caveats and trade-offs

The CGO 2025 paper (doi 10.1145/3696443.3708920, pp. 538-552), arXiv 2408.11456, the CGO slides on dse.in.tum.de and the Zenodo artifact (doi 10.5281/zenodo.13772996) were all unreachable here; per-core numbers come from search snippets only. The 5.1% is a mean with a ±4.0% spread on one core type; on the big cores the mean is 3.7% with a ±6.5% spread (spread larger than the mean), and only the in-order Cortex-A510 shows a large gain (33.9%). The win is against wasm64 software bounds checks, not against 32-bit Wasm with guard pages, which needs no explicit checks. Requires Arm MTE hardware (Pixel 8 class). README abstract (memory overhead &lt;5.3%) and BibTeX abstract (&lt;3.7%) disagree. wasmtime-mte is a research fork of bytecodealliance/wasmtime (12,557 commits, mostly upstream; last MTE commits 2026-01-14), not upstreamed; its README is the stock wasmtime README with no MTE instructions. [retier] The CGO 2025 paper, arXiv 2408.11456, the slides and the Zenodo artifact were all unreachable; per-core numbers come from search snippets only, and the benchmark harness is in the Zenodo artifact, not this repo. The 5.1% is a mean with a plus or minus 4.0% spread on one core type; on the big cores the mean is 3.7% with a 6.5% spread, and only the in-order Cortex-A510 shows a large gain (33.9%). The win is against wasm64 with software bounds checks in Wasmtime, not against 32-bit Wasm with guard pages. Sandbox strength, from reading the code: every MTE linear memory gets the same constant tag 1 (RUNTIME_MEM_TAG in crates/runtime/src/mte.rs, applied in crates/runtime/src/mmap/unix.rs), although the CGO slides (snippet) describe a distinct tag per sandbox; with mte_bounds_checks Cranelift emits no compare at all (bounds_checks.rs) and only with mem_safety is tag bit 56 forced back on, so a wasm64 index that reaches another instance's linear memory or any non-PROT_MTE mapping is not trapped, and the measured speedup partly reflects removed bounds checks rather than hardware-enforced isolation. The tag-check mode is per thread (prctl PR_SET_TAGGED_ADDR_CTRL) and set inside memory allocation, so Wasm code on a thread that never allocated a memory may run with tag checks ignored; copy-on-write memory images are disabled with MTE ('mte: avoid cow images with mte', January 2026); guard regions default to 0 when mte_bounds_checks is on. The base is Wasmtime 16.0.0 (upstream merge November 2023); commit titles such as 'Hacky fix for address_transform w/ mte' and three open 2023 PRs mark it as research code.

Needs Arm CPUs with MTE and PAC, 64-bit Wasm (memory64) modules, and the authors' forks of LLVM, wasmtime, wasm-tools and wasi-libc; the wasmtime fork carries the upstream Apache-2.0 LICENSE file but cage-meta has no LICENSE file. Primary purpose is memory safety; the speedup is a side effect of replacing software bounds checks.

## Maintenance

Research fork, Apache-2.0 WITH LLVM-exception, last commits 2026-01-14 (two MTE fixes) on a Wasmtime 16.0.0 base that has not been merged with upstream since November 2023; copyable for research on MTE hardware but not a maintained runtime.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** Peer-reviewed CGO 2025 paper (abstract reproduced in the cage-meta README) reports a sandboxing speedup of over 5.1% from MTE-based bounds checks; a search snippet of arXiv 2408.11456 ties it to PolyBench/C on a Google Pixel 8 against plain wasm64. Not A because the artifact (Zenodo) and paper were unreachable, so benchmark code, flags and per-core setup could not be opened.
- **Retiered** B to C: Enricher: the implementation gives every MTE linear memory the same constant tag and, in mte_bounds_checks mode, emits no bounds compare at all, so the measured 'MTE sandboxing' speedup over wasm64 software bounds checks comes from dropping the check without the per-sandbox tagging the paper describes (an out-of-bounds index reaching another instance's memory is not trapped); the paper and artifact remain unreachable and the per-core numbers are search snippets only. Measured configuration does less safety work than claimed (stb-zip precedent for a fast path that skips work): B to C.
- **Verifier notes:** Claim text in the record matches the cage-meta README exactly; hardware and per-core numbers added from search snippets of the arXiv version (marked snippet only). Keep at B; a paper-access retier could reach A if the Zenodo artifact names flags and harness. License is Apache-2.0 with LLVM exception (LICENSE file line 205).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `hardware`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-16 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/TUM-DSE/cage-meta/HEAD/README.md>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/README.md>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/CITATION.cff>
  - <https://github.com/TUM-DSE/wasmtime-mte>
  - <https://github.com/TUM-DSE/wasmtime-mte/commits>
  - <https://github.com/TUM-DSE/cage-meta>
  - <https://github.com/orgs/TUM-DSE/repositories?q=mte>
  - <https://github.com/orgs/TUM-DSE/repositories?q=cage>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/TUM-DSE/cage-meta/HEAD/README.md>
  - <https://github.com/TUM-DSE/wasmtime-mte>
  - <https://github.com/TUM-DSE/wasmtime-mte/commits>
  - <https://github.com/TUM-DSE/wasmtime-mte/commit/1129079>
  - <https://github.com/TUM-DSE/wasmtime-mte/commit/e4775b7>
  - <https://github.com/TUM-DSE/wasmtime-mte/commit/67d88cf>
  - <https://github.com/TUM-DSE/wasmtime-mte/commit/33bdf89>
  - <https://github.com/TUM-DSE/wasmtime-mte/pulls>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/cranelift/wasm/src/code_translator/bounds_checks.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/runtime/src/mte.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/runtime/src/mmap.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/runtime/src/mmap/unix.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/runtime/src/memory.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/runtime/src/cow.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/runtime/src/lib.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/cli-flags/src/lib.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/wasmtime/src/config.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/crates/environ/src/tunables.rs>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/TUM-DSE/wasmtime-mte/HEAD/CITATION.cff>
  - <https://github.com/TUM-DSE/llvm-memsafe-wasm>
  - <https://raw.githubusercontent.com/TUM-DSE/llvm-memsafe-wasm/HEAD/configure.sh>
  - <https://raw.githubusercontent.com/torvalds/linux/master/Documentation/arch/arm64/memory-tagging-extension.rst>
  - WebSearch: Cage hardware-accelerated safe WebAssembly MTE sandboxing (snippets of arXiv 2408.11456 and CGO 2025 slides)
  - https://themoonlight.io/review/cage-hardware-accelerated-safe-webassembly (DNS blocked)
  - https://arxiv.org/pdf/2408.11456v2 (DNS blocked)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tum-dse/wasmtime-mte`) · [data/wave13/enrich/raw/github_com_tum_dse_wasmtime_mte.json](../../../data/wave13/enrich/raw/github_com_tum_dse_wasmtime_mte.json) (enrichment confidence 0.6)

</details>
