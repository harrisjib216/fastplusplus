# picohttpparser-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Safe-Rust, ABI-identical rewrite of picohttpparser; beats scalar -O2 C only on header-heavy requests, loses on six of eight workloads.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | Rust/C time ratio per category: large headers 0.680 (Rust \~32% faster), upstream marker (\~620B/11 headers) 0.827 (Rust \~17% faster, flagged 'stability: CHECK'); but streaming 1.023 (near parity), typical 1.100, response 1.185, chunked 1.199, tiny 1.482, malformed 1.811 (all losses for Rust). Author also states native C with -march=native/pcmpestri beats scalar Rust by 1.45x, and -O3 regresses the Rust malformed-path result by 1.68x vs -O2. |
| **Workload** | Interleaved same-session microbenchmark (scripts/bench_compare.sh / bench_compare.c) timing a safe-Rust reimplementation vs the pinned C picohttpparser (commit f4d94b48) across 8 workload categories: tiny, typical (\~400B), large headers (\~4.9KB), response (\~150B), chunked decode, malformed input, streaming (8 staged prefixes), and an 'upstream marker' (\~620B, 11 headers) request. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-12400F (12 logical CPUs), Windows (Git-Bash/MSYS2 userland), custom power scheme, no CPU pinning, whole-loop clock_gettime timer (no p50/p95/p99) |
| **Compiler and flags** | C oracle: GCC 16.2.0 (w64devkit), anchor -O2 with C-side asserts live (NDEBUG unset), no -march so picohttpparser's SSE4.2/PCMPESTRI path is not compiled in; side tiers -O3 and -O3 -march=native via C_OPT. Rust: rustc 1.96.1, release profile opt-level=2, codegen-units=1, lto=true (side tiers RUSTFLAGS -C opt-level=3 / -C target-cpu=native). |
| **Adoption** | 2 stars |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/logicpl4gue/picohttpparser-rs) · [benchmark](https://github.com/logicpl4gue/picohttpparser-rs#speed) |

## Verdict

One same-session, interleaved whole-loop timer run on a single i5-12400F under Windows compared the Rust cdylib (rustc 1.96.1, opt-level=2, LTO, CGU1) with picohttpparser f4d94b48 built by GCC 16.2.0 at -O2 (no SSE4.2, asserts live): Rust was faster on the 64x64 B-header request (0.68) and on the bench.c \~620 B request (0.83), and slower on typical (1.10), response (1.18), chunked (1.20), tiny (1.48) and malformed (1.81), with streaming at parity (1.02). Six of the eight rows are flagged for &gt;5% trial spread, and against -O3 -march=native C at an older revision the bench.c request flips to C 1.45x faster.

## Use it when

- You link picohttpparser from C (or through FFI) and want a memory-safe parser behind the exact same ABI and behavior, with no changes at the call sites.
- Requests with many long, plain-ASCII header values (the 64 headers x 64 B, \~4.9 KB case): \~828 vs \~1,218 ns/parse against -O2 scalar C (0.68 ratio). It still led at -O3 (0.82).
- Header blocks like upstream bench.c's \~620 B / 11-header request, when your C build has no SSE4.2: \~166 vs \~201 ns/parse (0.83).
- You want hardened failure on caller contract violations. Null outputs, last_len &gt; len, or a corrupted chunked-decoder state give a defined -1/-2 instead of a segfault, an out-of-bounds read or a hang.

## Skip it when

- Speed is the goal and your picohttpparser is built with SSE4.2/-march=native. In the native tier (bench.c request), C with pcmpestri was 1.45x faster than Rust (\~138 vs \~200 ns/parse). This was recorded at an earlier revision (935b176), before the 16-byte SWAR change, and never re-run.
- Small or typical traffic: Rust was slower on tiny 37 B requests (1.48x), \~400 B requests (1.10x), \~150 B responses (1.18x) and 38 B chunked bodies (1.20x).
- Reject-fast / DoS-filter paths: rejecting at byte 1 takes 1.81x as long (\~5.7 vs \~3.1 ns). At opt-level=3 the Rust malformed path gets 1.68x worse, and the cause is still open.
- You need production maturity. The code was written in about a day (2026-09-08/09). There is one author, 2 stars, no CI, no tags and no crates.io release. It was built and tested only on one Windows machine with rustc 1.96.1. No real consumer (H2O/Plack/Furl) has been integrated, only a loopback TCP harness and a ctypes harness.
- Rust callers who want an idiomatic API: the only public interface is the unsafe extern "C" functions plus the repr structs, and the safe core modules are private.

## How it is fast

It is only faster on long header values, where get_token_to_eol runs a SWAR prescan: it loads 16 bytes as two u64 words, tests all 8 lanes of each word at once for any byte outside 0x20..0x7E, skips clean blocks and drops to the exact per-byte loop on a dirty one. C's scalar path (built without SSE4.2) checks one byte at a time in an 8x unrolled loop, so the SWAR scan wins on long runs of printable ASCII; the other change is a 256-entry tchar lookup table (measured \~11% faster than without it). The parser core has no unsafe code and uses bounds-checked .get() reads. Each export pays for catch_unwind, and in the benchmark each call also went through a DLL import hop; that fixed cost is why tiny and reject-fast inputs are slower.

## Compared with alternatives

The vkrasnov AVX2 fork (1.68-1.79x), httpp (\~2.26x at -O3) and hparse (\~12.5% wall-clock) are all reported faster than picohttpparser overall, while this one wins only on header-heavy inputs against scalar -O2 C. Pick it when you want memory-safe code behind picohttpparser's exact ABI and behavior; pick a sibling when speed is the goal.

## Integration

| | |
|---|---|
| **Form** | crate (cdylib + staticlib + rlib); not on crates.io, build from git |
| **Dependencies** | none |
| **Minimum toolchain** | Rust edition 2024 (rust-version = 1.85 is a declared floor only; only rustc 1.96.1 was ever run) |
| **Platforms** | Portable Rust with no arch intrinsics or SIMD. Layout asserts only on 64-bit targets. Tested only on Windows x86-64 (i5-12400F); 32-bit and non-Windows builds are not exercised. |
| **Thread safety** | Not stated explicitly. The parse functions are stateless and write only to caller-owned outputs, and the only static is an immutable lookup table. Chunked-decoder state lives in a caller-owned struct (one per stream), as in upstream. |
| **Drop-in for the baseline** | partial: same 5 symbols, header and struct layout, and matches C on all 133,352 differential cases. It deliberately differs on 4 contract-violation inputs (D001-D004: returns -1/-2/0 where C faults, reads out of bounds or hangs). It has no SSE4.2 fast path. |

## Gotchas

- The README's 'segfault' framing is about caller contract violations: null pointers, last_len &gt; len, a forged decoder _state, and a NULL is_in_data query. Differential fuzzing of hostile bytes (\~1.94M executions) recorded 0 crashes on either side.
- Memory safety stops at the FFI seam. Each export builds a slice with slice::from_raw_parts(buf, len), so a wrong (buf, len) from the caller is still undefined behavior, exactly as in C.
- Keep the pinned release profile (opt-level=2, LTO, codegen-units=1, overflow-checks off, panic=unwind). Raising opt-level to 3 regressed the malformed path 1.68x. A panic inside a parser is caught at the seam and returned as -1.
- Every published Rust number came through the DLL, because MinGW ld could not link the MSVC-built staticlib. Rust callers linking the rlib get cross-crate inlining and will see different numbers.

## Known shortcomings

- Mostly not faster: its two wins are only against picohttpparser built at -O2 with the SSE4.2 path off, 6 of 8 workloads are losses, 6 of 8 rows are flagged unstable (&gt;5% spread), and in its own native-flags run C beats Rust 1.45x on the upstream request.
- Every Rust number went through a DLL while C was linked directly (different toolchains). The native-flags loss predates the SWAR change and was never re-run. The 'upstream segfaults' pitch is overstated: all divergences are caller mistakes and fuzzing found no crashes on either side. Written in about a day, not on crates.io, no CI, tested on one Windows machine; the only public API is unsafe extern "C".

## Caveats and trade-offs

The two wins are against picohttpparser built -O2 without SSE4.2, i.e. its scalar path. In the same-session native tier (results/bench-compare-native.json: C -O3 -march=native vs Rust -C target-cpu=native, upstream bench.c request), C is 1.45x faster than Rust, so the 0.827 upstream-marker win flips to a loss once the baseline's SIMD path is on. At the -O3 tier, large headers is still a win (0.8165). In results/bench-compare.json, 6 of 8 rows, including large headers (0.6803), are flagged stability 'CHECK-spread&gt;5%', not only the upstream-marker row the README flags. The author calls the numbers 'internal-engineering' and 'not portable'. The project pitches memory safety and parity with the C (133,352/133,352 differential cases), not speed: 6 of 8 workloads lose. Extremely new (created 2026-09-09, 2 stars, single author, no CI).

Rust only wins on 2 of 8 published workloads (large headers, upstream marker); it loses on the other 6, including a 1.8x fixed-cost floor on malformed/reject-fast input. No SIMD path yet ('SIMD prize' explicitly parked/unimplemented), so it cannot match C built with -march=native + PCMPESTRI. Real-consumer integration (H2O/Plack/Furl) is parked, not done.

## Maintenance

Active but brand-new (created 2026-09-09; the last commit, 2026-09-11, was README-only), single-author, MIT and 1,527 lines with no dependencies, so it is easy to vendor, though it has no releases or CI and its author presents it as a correctness and safety experiment, not a speed claim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README #speed table gives the 8 Rust/C ratios exactly as claimed (0.680, 0.827, 1.023, 1.100, 1.185, 1.199, 1.482, 1.811) against pinned h2o/picohttpparser f4d94b48, and results/bench-compare.json holds the same values (large 0.6803, anchor 0.8267). The code is public (scripts/bench_compare.sh + scripts/bench_compare.c + scripts/bench_corpus.h), and GCC 16.2.0 -O2, rustc 1.96.1 opt-level=2/LTO/CGU1 and an i5-12400F are all stated (README + docs/methodology.md), which meets tier A.
- **Verifier notes:** Numbers and metadata check out (MIT, not a fork, 2 stars, last commit 2026-09-11, active). I kept this as confirm because the README does publish workload-specific wins against the named baseline, but it is borderline 'not faster': the wins exist only against scalar -O2 C and vanish against -march=native C. The orchestrator may want to tag it mixed or workload-specific, or drop it as not-faster.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/logicpl4gue/picohttpparser-rs>
  - <https://github.com/logicpl4gue/picohttpparser-rs#speed>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/docs/methodology.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/scripts/bench_compare.sh>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/scripts/bench_corpus.h>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/README.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/bench-compare.json>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/bench-compare-native.json>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/bench-compare-o3.json>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/reference/PINNED.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/Cargo.toml>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/logicpl4gue/picohttpparser-rs>
  - <https://github.com/logicpl4gue/picohttpparser-rs#speed>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/Cargo.toml>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/src/lib.rs>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/src/core.rs>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/src/request.rs>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/src/ffi.rs>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/docs/api.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/docs/compatibility.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/docs/divergences.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/docs/methodology.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/README.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/EVIDENCE.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/bench-compare.json>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/bench-compare-o3.json>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/results/bench-compare-native.json>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/scripts/bench_corpus.h>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/reference/PINNED.md>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/reference/picohttpparser.c>
  - <https://github.com/logicpl4gue/picohttpparser-rs/blob/main/tests/abi.rs>
  - <https://github.com/logicpl4gue/picohttpparser-rs/commits/main>
  - <https://github.com/logicpl4gue/picohttpparser-rs/issues>
  - <https://github.com/h2o/picohttpparser/commits/master>
  - <https://crates.io/api/v1/crates/picohttpparser-rs>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/logicpl4gue/picohttpparser-rs`) · [data/wave5/enrich/raw/github_com_logicpl4gue_picohttpparser_rs.json](../../../data/wave5/enrich/raw/github_com_logicpl4gue_picohttpparser_rs.json) (enrichment confidence 0.55)

</details>
