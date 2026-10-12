# WebAssembly memory.copy (bulk-memory-operations proposal)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Study only · `WebAssembly (proposal text with V8 prototype)` · `Per-directory (repo LICENSE): document/ W3C Software and Document Notice and License; interpreter/ and test/ Apache-2.0; papers/ CC-BY-4.0` · 🔵 finished

> WebAssembly memory.copy/memory.fill instructions; 2017 V8 prototype copied up to about 3-11x faster than Emscripten's wasm memcpy loop.

| | |
|---|---|
| **Beats** | Emscripten-generated wasm memcpy loop (aligned i32.load/i32.store) used in the Unity demo, plus manually unrolled i32 and i64 load/store loop variants |
| **Claimed result** | At 128 KiB: memory.copy 29.728 Gib/s vs i64 load/store x4 10.032, i64 x2 7.934, i32 x2 3.975, plain i32 loop 2.782 Gib/s. At 1.0 KiB: 17.902 vs 7.010, 6.112, 3.568, 2.614 Gib/s. Loses at 32 B: intrinsic 1.382 vs i64 x4 1.565 Gib/s. At 1 MiB: 11.760 vs 10.091 Gib/s. |
| **Workload** | Each row copies 1 GiB in total with a V8 prototype where memcpy/memmove exports are replaced by memory.copy, versus the wasm loops; copy sizes 32 B to 1 MiB within a 1 MiB working set. |
| **Metric** | throughput |
| **Hardware** | x86_64, 2.9 GHz, L1 32k, L2 256k, L3 256k (CPU model not stated) |
| **Adoption** | 82 stars, 21 forks; archived Nov 3 2021; finished proposal merged into WebAssembly core spec 2.0 per WebAssembly/proposals finished-proposals.md |
| **Last commit** | 2021-03-31 |
| **Links** | [repository](https://github.com/WebAssembly/bulk-memory-operations) · [benchmark](https://github.com/WebAssembly/bulk-memory-operations/blob/master/proposals/bulk-memory-operations/Overview.md) |

## Verdict

Ben Smith's 2017 measurement in the proposal Overview copies 1 GiB per row (32 B to 1 MiB chunks) with a hacked V8 that runs memory.copy as a native MemMove call, against Emscripten's i32 memcpy loop and hand-unrolled i32/i64 loops, on an unnamed 2.9 GHz x86-64 machine: 17.902 vs 7.010 GiB/s (best loop) at 1 KiB, 29.728 vs 10.032 at 128 KiB, and a loss at 32 B (1.382 vs 1.565).

## Use it when

- Any Wasm build that copies or clears buffers larger than a few dozen bytes (image, audio and network buffers, Vec/std::vector growth, arena resets): make sure bulk memory is on so memcpy, memmove and memset become memory.copy and memory.fill.
- Toolchains already default to it: Emscripten 4.0.0 (2025-01-14) enables BULK_MEMORY and implements memcpy and memmove as memory.copy; Rust 1.87+ with LLVM 20 enables bulk-memory on wasm32-unknown-unknown; wasi-libc's memcpy switches to it above 32 bytes.
- Overlapping moves (memmove) in Wasm: the instruction defines overlap semantics, whereas the 2017 Emscripten memmove fell back to a backward byte loop for overlapping regions.
- Passive data segments with memory.init plus data.drop for initialising shared memory once in threaded Wasm (the proposal's other half).

## Skip it when

- Tiny copies: at 32 B the prototype intrinsic did 1.382 GiB/s against 1.565 for the unrolled i64 loop; LLVM avoids memory.copy for short constant-length copies and wasi-libc only calls it above 32 bytes (issue #111 cites Firefox's out-of-line memcpy as up to 5x slower than a wasm-written one).
- Targets that must run on pre-2.0 engines: modules containing the 0xfc-prefixed bulk instructions fail validation there; Rust's wasm32v1-none target and -mno-bulk-memory -mno-bulk-memory-opt in Emscripten exist for that.
- As evidence about native performance: the comparison is native memmove against scalar 2017 wasm loops without SIMD, not against libc memcpy or a wasm simd128 loop.
- Code that relies on non-overlap for speed: there is no non-overlapping variant (issue #121 stayed open), so engines always handle the memmove case.

## How it is fast

Instead of a wasm-compiled byte/word loop with a bounds check per access, the engine handles the whole range in one call to its native memmove (the prototype called V8's MemMove), which can use the host CPU's widest vector moves. The proposal's table shows the gain growing with size: a loss at 32 B, 1.2x at 64 B, 2.5x the best hand-unrolled i64 loop at 1 KiB and 3x at 128-512 KiB, against the Emscripten i32 loop 6.8x at 1 KiB and 10.7x at 128 KiB.

## Compared with alternatives

Inside Wasm, use bulk memory for memcpy, memmove and memset and the opt-in wasi-libc simd128 string routines for memchr, strlen and strcmp-style scans; the native siblings (tinymembench kernels, Arm Optimized Routines, AOCL-LibMem) apply only to native builds, and memory.copy in browsers already ends in the host's native memmove.

## Integration

| | |
|---|---|
| **Form** | WebAssembly core instruction (spec 2.0), emitted by compilers; no library to link |
| **Dependencies** | none; an engine implementing bulk memory and a compiler flag (-mbulk-memory in clang, default in Emscripten 4.0.0+ and in Rust 1.87+/LLVM 20 for wasm32-unknown-unknown) |
| **Minimum toolchain** | Emscripten 4.0.0 by default (earlier with -mbulk-memory); Rust 1.87.0 with LLVM 20 by default on wasm32-unknown-unknown; wasi-libc built with -mbulk-memory uses it for copies over BULK_MEMORY_THRESHOLD (32 bytes by default) |
| **Platforms** | Any WebAssembly 2.0 engine; Emscripten 6.0.9 (2026-09-01) raised its minimum Safari to 15.0 and now assumes bulk memory in every supported engine. Speed depends on each engine's native memmove and call path. |
| **Thread safety** | not documented in the proposal text |
| **Drop-in for the baseline** | partial — a compiler switch replaces the libc memcpy/memmove/memset bodies transparently, but it is an engine feature, not a function you can call from portable C++ outside Wasm |

## Gotchas

- The intrinsic column cannot be reproduced from the public gist: the 'intrinsic' module's exported _memcpy body just returns 0 and was swapped for memory.copy only by the author's unpublished V8 hack, so running memcpy.js on a stock engine times empty calls; the gist's data initialisation and 'Value mismatch' verification are commented out and each cell is a single timed pass (one-tenth warm-up, no repeats).
- Units are mislabelled: the table says 'Gib/s', but the gist computes (bytes copied x 1000) / (ms x 1024^3), so the numbers are gibibytes per second; the unexplained drop from 29.994 at 512 KiB to 11.760 at 1 MiB comes from one run on a machine with no CPU model, engine version or flags stated.
- Every row only touches a 1 MiB source and 1 MiB destination window with aligned, non-overlapping offsets, so the Emscripten loop's misaligned byte path and the overlap path were never exercised.
- Since 2019 (spec PR #123, after issue #111) memory.copy checks bounds before writing and traps on out-of-bounds even for zero length; Emscripten's memcpy and memmove therefore skip the instruction when n is 0.

## Known shortcomings

- Every number matches Overview.md but the baseline is Emscripten wasm loops, not native libc; the benchmark gist has verification commented out and the intrinsic column needs the author's unpublished V8 hack; no CPU model. Proposal merged into the core spec 2.0 (finished).
- Harness flaws: the public gist's 'intrinsic' module is a stub returning 0 (a stock engine times empty calls; memory.copy was swapped in only by the author's unpublished V8 hack), the verification block is commented out, each cell is one timed pass, 'Gib/s' is really GiB/s, and the drop at 1 MiB is unexplained. The baseline is a scalar 2017 wasm loop, not libc. memory.copy is now the default lowering in Emscripten 4.0.0 and Rust 1.87 / LLVM 20; wasi-libc uses it only above 32 B, matching the 32 B loss.

## Caveats and trade-offs

Baseline is a 2017-era Emscripten wasm memcpy (gist c57dc945, memcpy.wast: byte prologue to 4-byte alignment, i32.load/i32.store word loop, byte tail; byte path when src and dst alignments differ) plus hand-unrolled variants, not a native libc memcpy; the prototype memory.copy simply called V8's native MemMove, so this is native memmove versus wasm-compiled loops. The benchmark gist (b8e8bc0c, memcpy.js, created 2017-10-26) is public, but its data initialisation and verification block is commented out, and the 'intrinsic' module's exported _memcpy body is a stub returning 0 that only the author's hacked V8 replaced with memory.copy, so the intrinsic column cannot be reproduced on a stock engine from the gist; the size-dependent curve (1.382 Gib/s at 32 B rising to 29.994 at 512 KiB, falling to 11.760 at 1 MiB) is consistent with real copying, not a no-op. Engine version, CPU model and flags are not given, and the stated 'L3 256k' looks mis-stated. Single first-party run. The repository is archived (2021-11-03); WebAssembly/proposals finished-proposals.md lists Bulk memory operations as finished and merged into core spec 2.0 (WG 2021-02-10), so memory.copy is now a standard instruction implemented by engines rather than a library.

A proposal text plus a hacked V8 prototype, not a library. The repo's LICENSE file points to per-directory licences (document/ under the W3C Software and Document Notice and License). The instruction itself is a runtime feature, so the benefit applies only to engines that call native MemMove for memory.copy.

## Maintenance

Finished: merged into the WebAssembly core spec 2.0 (WG vote 2021-02-10) and the repository archived 2021-11-03; the instruction is now the default lowering of memcpy in Emscripten 4.0.0+ and Rust 1.87+, so it is reference material, not code to copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The Overview.md table matches every quoted number (memory.copy intrinsic vs the Emscripten i32 loop and hand-unrolled i32/i64 loops); it is the proposal author's own run with the benchmark in a public gist, but the CPU model, V8 version and flags are not stated and the intrinsic needs the author's unpublished V8 hack, so C.
- **Verifier notes:** Numbers verified exactly against Overview.md; tier C stands, usability stays reference (an engine instruction, not copyable library code). Shortcomings: off-baseline (wasm loops, not native libc), benchmark gist has verification commented out and needs an unpublished V8 hack for the intrinsic column, no CPU model or engine version. maintenance_status set to finished because the WebAssembly CG lists the proposal as finished and archived the repo after merge; revert to abandoned if archived-means-abandoned is preferred.
- **Fields the verifier corrected:** `caveats`, `license`, `stars_or_usage`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-35 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/WebAssembly/bulk-memory-operations>
  - <https://github.com/WebAssembly/bulk-memory-operations/commits/master>
  - <https://raw.githubusercontent.com/WebAssembly/bulk-memory-operations/HEAD/proposals/bulk-memory-operations/Overview.md>
  - <https://raw.githubusercontent.com/WebAssembly/bulk-memory-operations/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/WebAssembly/bulk-memory-operations/HEAD/README.md>
  - <https://raw.githubusercontent.com/WebAssembly/proposals/HEAD/finished-proposals.md>
  - <https://gist.github.com/binji/b8e8bc0c0121235d9f1668bc447c7f8c>
  - <https://gist.github.com/binji/c57dc945bba60985439ef8e5b574eee0>
- **Sources the enricher read:**
  - <https://github.com/WebAssembly/bulk-memory-operations>
  - <https://raw.githubusercontent.com/WebAssembly/bulk-memory-operations/HEAD/proposals/bulk-memory-operations/Overview.md>
  - <https://raw.githubusercontent.com/WebAssembly/bulk-memory-operations/HEAD/README.md>
  - <https://raw.githubusercontent.com/WebAssembly/bulk-memory-operations/HEAD/LICENSE>
  - <https://github.com/WebAssembly/bulk-memory-operations/issues?q=is%3Aissue>
  - <https://github.com/WebAssembly/bulk-memory-operations/issues/111>
  - <https://github.com/WebAssembly/bulk-memory-operations/issues/121>
  - <https://raw.githubusercontent.com/WebAssembly/proposals/HEAD/finished-proposals.md>
  - <https://gist.github.com/binji/b8e8bc0c0121235d9f1668bc447c7f8c>
  - <https://gist.github.com/binji/c57dc945bba60985439ef8e5b574eee0>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/HEAD/system/lib/libc/emscripten_memcpy.c>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/HEAD/system/lib/libc/emscripten_memmove.c>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/HEAD/system/lib/libc/emscripten_memset.c>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/HEAD/libc-top-half/musl/src/string/memcpy.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/HEAD/libc-top-half/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/src/doc/rustc/src/platform-support/wasm32-unknown-unknown.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/webassembly/bulk-memory-operations`) · [data/wave13/enrich/raw/github_com_webassembly_bulk_memory_operations.json](../../../data/wave13/enrich/raw/github_com_webassembly_bulk_memory_operations.json) (enrichment confidence 0.7)

</details>
