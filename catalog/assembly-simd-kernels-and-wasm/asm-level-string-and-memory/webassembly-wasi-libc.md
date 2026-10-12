# wasi-libc SIMD string routines (opt-in, wasm simd128)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0 WITH LLVM-exception; Apache-2.0; MIT` · 🟢 active

> Opt-in wasm simd128 versions of strlen, memchr, strchr, strrchr, memcmp, strspn and strcspn in wasi-libc, replacing musl's scalar loops.

| | |
|---|---|
| **Beats** | wasi-libc's own scalar string.h routines (musl-derived SWAR on a 32-bit size_t), i.e. the same library compiled to wasm without -DSIMD=ON |
| **Claimed result** | ncruces, issue #580 (May 9, 2025), 'Numbers are rough, and only for wazero': memchr 4.3x, memcmp 10.0x, strlen 4.9x, strchr 4.2x, strrchr 9.9x, strcmp 12.8x, strncmp 16.3x, strspn 9.1x, strcspn 9.7x, strstr 5.6x, geomean 7.8x over musl's SWAR versions. These were measured on ncruces's go-sqlite3 libc (sqlite3/libc/string.h), not on a wasi-libc build. wasi-libc main has opt-in SIMD versions only of strlen (#586), memchr (#592), strchrnul and hence strchr (#594), memrchr and hence strrchr (#598), memcmp (#603) and strspn/strcspn (#597); strcmp, strncmp and strstr are still the scalar musl code, so the 12.8x, 16.3x and 5.6x figures do not apply to wasi-libc. July 2, 2025: with the #586 strlen gist changed to 10-byte strings, 'the improvement (using wasmtime on amd64) is still around 2x'. |
| **Workload** | Per-function speedup of wasm simd128 string.h routines over musl's scalar SWAR code, run from Go under the wazero runtime (go-sqlite3 GitHub Actions run 14516931864, x86-64 and AArch64), string sizes not stated (a reviewer asked whether a 4 MB string from libc_test.go was used); plus strlen on 10-byte strings under wasmtime on amd64. |
| **Metric** | throughput |
| **Hardware** | Not stated for the table (issue cites x86-64 and AArch64 GitHub Actions runners under wazero; the 10-byte strlen run was wasmtime on amd64). In PR #592 ncruces measured with wasmtime on a Xeon W-2135 and found the any_true versus bitmask difference 'hard to measure'. |
| **Compiler and flags** | Built with wasm simd128 (README CMake option -DSIMD=(ON\|OFF)); compiler and flags for the benchmark not stated |
| **Adoption** | about 1.0k stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/WebAssembly/wasi-libc) · [benchmark](https://github.com/WebAssembly/wasi-libc/issues/580) |

## Verdict

The only per-function table (memchr 4.3x, memcmp 10.0x, strlen 4.9x, strchr 4.2x, strrchr 9.9x, strspn 9.1x, strcspn 9.7x over the musl scalar code) is a rough comment by the contributor in issue #580, measured with Go under wazero on GitHub Actions x86-64 and AArch64 runners against his go-sqlite3 libc, with no CPU model, string sizes, compiler or flags; PR #586 adds about 3x strlen and 2x memchr on mixed lengths (7x and 5x on large inputs) and about 2x for 10-byte strlen under wasmtime on amd64. The SIMD-versus-scalar comparison is wasm-to-wasm within the same libc, not against native glibc.

## Use it when

- You build your own wasi-libc sysroot (wasi-sdk does not pass -DSIMD=ON) and your runtime supports simd128 (and relaxed-simd for strspn/strcspn).
- String-heavy C code compiled to wasm, such as SQLite, parsers or text tools, where strlen/memchr/strchr scans over strings of tens of bytes or more dominate.
- memcmp-heavy code on buffers of 16 bytes or more, and strrchr or memrchr scans, where the musl fallback is a byte-at-a-time loop and the SIMD gain is largest.
- Hosts on AArch64 or x86-64 with a JIT/AOT runtime (wasmtime, wazero, V8) that lowers v128 ops to NEON or SSE.

## Skip it when

- Your toolchain is Clang 19 or 20: strlen, memchr, strchr, strspn and strcspn silently fall back to scalar (llvm/llvm-project#146574 ICE guard); only memcmp and memrchr/strrchr get SIMD.
- You need strcmp, strncmp, strstr, memmem or strcasecmp speedups: those stay scalar musl code in wasi-libc (the larger numbers in issue #580 came from ncruces's separate go-sqlite3 libc).
- Interpreted or non-SIMD wasm runtimes, or runtimes without relaxed-simd: a module containing i8x16.relaxed_swizzle (strspn_simd.c) will fail validation.
- Very short strings or calls dominated by host/call overhead; the only small-string data point is about 2x for 10-byte strlen under wasmtime, and no per-size table exists.
- You want a stock prebuilt sysroot: the SIMD build is opt-in and off by default, so using it means maintaining a custom wasi-libc build.

## How it is fast

Each routine scans 16 bytes per step with v128 compares (i8x16.eq) and a cheap any_true/all_true test, only computing i8x16.bitmask plus ctz/clz once a hit is found, because bitmask lowers poorly on AArch64. strlen, memchr, strchrnul, strspn and strcspn load aligned 16-byte blocks (reading slightly before and after the object, safe because wasm memory is bounds-checked at 64 KiB page granularity) through inline assembly so the compiler cannot treat the over-read as UB; memcmp and memrchr use unaligned v128 loads strictly inside [0, n). strspn/strcspn use the Langdale/Mula nibble-bitmap byte-set lookup (the same idea as Hyperscan's truffle) with two i8x16.swizzle table lookups per block.

## Compared with alternatives

Pick it whenever the target is wasm and the libc is wasi-libc: Arm Optimized Routines, AOCL-LibMem and the other native siblings cannot be used inside a wasm module, and the WebAssembly memory.copy entry only covers memcpy/memmove/memset, not search and compare routines. For native code use Arm Optimized Routines or the host glibc instead.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none beyond wasi-libc's own build (clang with the wasm32 target, compiler-rt builtins) |
| **Minimum toolchain** | Clang 10+ for wasi-libc; SIMD string paths need Clang 21+ (Clang 19/20 compile the scalar fallback for the inline-asm routines); build flags -msimd128 -mrelaxed-simd -mbulk-memory |
| **Platforms** | wasm32 (wasip1, wasip2, wasip1-threads, ...) on runtimes with simd128; relaxed-simd needed for the SIMD strspn/strcspn |
| **Thread safety** | Pure functions with no shared state; thread-safe like the scalar versions |
| **Drop-in for the baseline** | yes |

## Gotchas

- Test-coverage gap: wasi-libc's only SIMD CI job ('Test wasm32-wasi-simd', -DSIMD=ON) uses clang_version 20, which compiles out the inline-asm SIMD paths, so upstream CI exercises only the SIMD memcmp and memrchr; strlen, memchr, strchrnul, strspn and strcspn SIMD code is validated only by the contributor's Go tests and fuzzing and by abrown's out-of-tree fuzzing.
- Latent C undefined behaviour in strspn_simd.c's __wasm_v128_setbit: bitmap-&gt;hi[lo_nibble] |= (uint8_t)(1u &lt;&lt; (hi_nibble - 8)) shifts by a negative count for every byte below 0x80. It works today only because wasm's i32.shl masks the count to 5 bits, giving 1&lt;&lt;24..31 which truncates to 0; the shift line came up in PR #597 review but UB was not discussed.
- The 'over musl's SWAR' framing is only true for strlen, memchr and strchrnul: the scalar memcmp, memrchr, strcmp and strncmp in wasi-libc are byte-at-a-time loops and strspn/strcspn use a bitset loop, which is why memcmp (10.0x) and strrchr (9.9x) show the largest gains.
- memcmp and memrchr SIMD assume the whole n-byte range is readable: abrown's fuzzing found a 16-byte memcmp near the end of memory that traps in the SIMD version while the scalar version returns early (invalid input either way; documented in the source comment).

## Known shortcomings

- Scope overstated: the issue #580 numbers measure ncruces's go-sqlite3 libc; wasi-libc main has SIMD only for strlen, memchr, strchr, strrchr, memcmp, strspn and strcspn, so the strcmp 12.8x, strncmp 16.3x and strstr 5.6x figures do not apply; SIMD is off by default; the baseline is wasm against wasm, not glibc.
- Harness and coverage flaw: upstream's only SIMD CI job ('Test wasm32-wasi-simd', -DSIMD=ON) builds with clang 20, and the Clang 19/20 guard compiles out the SIMD paths of strlen, memchr, strchrnul, strspn and strcspn, so CI tests only the SIMD memcmp and memrchr. Latent C UB in strspn_simd.c __wasm_v128_setbit: '1u &lt;&lt; (hi_nibble - 8)' is a negative shift for bytes below 0x80 (works only because wasm i32.shl masks the count). 'Over musl SWAR' holds only for strlen, memchr and strchrnul; the scalar memcmp, memrchr, strcmp and strncmp are byte loops, which explains the 10x gains. -DSIMD=ON also needs relaxed-simd at runtime (strspn/strcspn); wasi-sdk does not enable SIMD; the go-sqlite3 libc directory is 404 (project moved to wasm2go).

## Caveats and trade-offs

Numbers are one rough comment in a tracking issue, measured on the contributor's go-sqlite3 implementations rather than the code later merged into wasi-libc, with no CPU, runtime version, compiler, flags or string sizes; a reviewer asked whether the table used a 4 MB string and the reply gave no size, only saying small calls are hard to measure from the host and that 'there are too many variables (Wasm runtime, CPU architecture, string length), to give any hard guarantees'. Only strlen, memchr, strchr, strrchr, memcmp, strspn and strcspn have SIMD paths in wasi-libc; strcmp, strncmp and strstr stay scalar. The SIMD routines are off by default (-DSIMD=ON, __wasilibc_simd_string), and strspn/strcspn SIMD is skipped on Clang 19 and 20 (llvm/llvm-project#146574 ICE). The baseline is wasm-to-wasm (scalar vs SIMD in the same libc), not native glibc. The go-sqlite3 libc README with updated numbers linked from the issue now returns 404.

Opt-in at build time (-DSIMD=ON) and needs a runtime with wasm simd128; functions landed one by one: strlen (#586), memchr (#592), strchrnul (#594), strspn/strcspn (#597), memrchr (#598), memcmp (#603); memchr was switched to inline assembly after an undefined-behaviour concern about pointer arithmetic (#593).

## Maintenance

Actively maintained WebAssembly-organisation project (commits through 2026-10-01) under Apache-2.0 WITH LLVM-exception, Apache-2.0 and MIT; the SIMD routines landed between June and December 2025 and remain opt-in, with maintainers asking for real-world users before considering enabling them by default.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** The only numbers are one comment by the code's contributor in issue #580, measured on his own go-sqlite3 SIMD libc under wazero via a GitHub Actions run, with no CPU, runtime version, compiler, flags or string sizes; first-party without methodology, so C. Downgraded for scope: three of the ten listed routines are not SIMD in wasi-libc at all.
- **Verifier notes:** Issue #580 table matches the record, but it measures ncruces's go-sqlite3 libc; wasi-libc main (checked in libc-top-half/musl/src/string) merged SIMD only for strlen, memchr, strchrnul, memrchr, memcmp and strspn/strcspn, so strcmp/strncmp/strstr claims are dropped from scope. Tier stays C. Metadata confirmed: \~1.0k stars, 255 forks, last commit 2026-10-01, Apache-2.0 WITH LLVM-exception / Apache-2.0 / MIT, active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-28 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/WebAssembly/wasi-libc>
  - <https://github.com/WebAssembly/wasi-libc/commits>
  - <https://github.com/WebAssembly/wasi-libc/issues/580>
  - <https://github.com/WebAssembly/wasi-libc/pull/592>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/README.md>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strlen.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/memchr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/memcmp.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strchrnul.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/memrchr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strrchr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strcmp.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strncmp.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strstr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strspn.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strcspn.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strspn_simd.c>
  - <https://github.com/ncruces/go-sqlite3/tree/main/sqlite3/libc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/README.md>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strlen.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/memchr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/memcmp.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strchrnul.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/memrchr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strrchr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strchr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strcmp.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strncmp.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strstr.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strspn.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strcspn.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-libc/main/libc-top-half/musl/src/string/strspn_simd.c>
  - <https://raw.githubusercontent.com/WebAssembly/wasi-sdk/main/cmake/wasi-sdk-sysroot.cmake>
  - <https://github.com/WebAssembly/wasi-libc/issues/580>
  - <https://github.com/WebAssembly/wasi-libc/issues?q=simd>
  - <https://github.com/WebAssembly/wasi-libc/pull/586>
  - <https://github.com/WebAssembly/wasi-libc/pull/592>
  - <https://github.com/WebAssembly/wasi-libc/pull/593>
  - <https://github.com/WebAssembly/wasi-libc/pull/597>
  - <https://github.com/WebAssembly/wasi-libc/pull/603>
  - <https://github.com/ncruces/go-sqlite3/tree/main/sqlite3/libc>
  - <https://github.com/ncruces/go-sqlite3>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/webassembly/wasi-libc`) · [data/wave13/enrich/raw/github_com_webassembly_wasi_libc.json](../../../data/wave13/enrich/raw/github_com_webassembly_wasi_libc.json) (enrichment confidence 0.75)

</details>
