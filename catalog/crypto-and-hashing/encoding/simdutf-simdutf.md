# simdutf Base64 (WHATWG forgiving-base64, ignorable-character SIMD decoding)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 OR MIT` · 🟢 active

> SIMD WHATWG forgiving-base64 codec in the simdutf C++ library; its fastbase64 CLI decodes 100 MB 3.5–27x faster than system base64.

| | |
|---|---|
| **Beats** | base64 |
| **Claimed result** | README fastbase64 table (median wall-clock ms from scripts/base64bench.sh, decoding 100 MB of random data): Apple M4 Max 1433.5 ms for the system base64 vs 52.7 ms for fastbase64 (about 27x), and Xeon Gold 6548N on Linux 291.8 ms vs 84.4 ms (about 3.5x) (derived from page data). At 1 MB the two are near parity. The Lemire 2025 preprint abstract says only that the new functions 'multiply the base64 decoding speed compared to traditional methods', with no factor given. |
| **Workload** | Command-line base64 decoding (and encoding) of 1, 10 and 100 MB random files with simdutf's fastbase64 tool, which uses simdutf's forgiving-base64 decoder, against the OS base64 utility (GNU coreutils on Linux, BSD/macOS base64 otherwise). The ignorable-character SIMD algorithm itself is described in Lemire's Authorea preprint (DOI 10.22541/au.175692137.72576748/v1). |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max; Intel Xeon Gold 6548N (Linux) |
| **Adoption** | 1,979 stars; used in Node.js, WebKit/Safari, Chromium, Ladybird, Bun, Cloudflare Workers, Ghostty |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/simdutf/simdutf) · [benchmark](https://github.com/simdutf/simdutf#performance) |

## Verdict

The only first-party numbers are end-to-end CLI timings from scripts/base64bench.sh: the median of 10 runs on random 1/10/100 MB files, fastbase64 (no wrapping) against the OS base64. At 100 MB, decode is 52.7 vs 1,433.5 ms on an Apple M4 Max (macOS base64) and 84.4 vs 291.8 ms on a Xeon Gold 6548N (GNU base64), with no compiler or flags stated. Each timing includes a python3 interpreter start (the script timestamps with `python3 -c`), and on Linux GNU base64 decodes its own 76-column wrapped output. Separately, Lemire's in-browser test (Apple M4, 64 KiB blocks) has Chrome, whose V8 Uint8Array base64 builtins call simdutf, at 19 GB/s encode and 4.6 GB/s decode, against 0.34/0.40 GB/s for the older Firefox.

## Use it when

- Decoding web-style base64 (atob semantics, data: URLs, JSON fields, MIME/PEM text with line breaks) where the input may contain spaces or newlines that would force a strict SIMD codec to reject it or fall back to scalar.
- When you need base64url, padding control, strict canonical checks (BASE64_EXTRA_BITS) or chunked decoding (stop_before_partial plus base64_to_binary_details) in one library. These are the functions that Node.js atob and V8's Uint8Array.fromBase64/toBase64 call.
- Encoding MIME-style wrapped output directly (binary_to_base64_with_lines) rather than encoding and then inserting newlines in a second pass.
- Replacing the base64 CLI on files of 10 MB or more: in the README's run, 100 MB decodes in 52.7 ms against 1,433.5 ms for macOS base64 on an M4 Max, and in 84.4 ms against 291.8 ms for GNU base64 on a Xeon Gold 6548N.
- Projects that already link simdutf, or C++17 projects that can vendor the two-file amalgamation built with --with-base64 to leave out the UTF code.

## Skip it when

- Small one-off CLI jobs: at 1 MB, fastbase64 and the system tool are at parity in the README table (e.g. 13.7 vs 12.8 ms decode on Linux), because process startup dominates.
- When you need strict RFC 4648 rejection by default. The default loose mode ignores whitespace, accepts missing padding, and decodes 'ZXhhZg==', 'ZXhhZg' and 'ZXhhZh==' to the same bytes. You must pass last_chunk_handling_options::strict to reject the last two.
- Pure-C codebases without a C++17 toolchain: the C API (C11) is a thin wrapper over the C++ build and is labelled experimental.
- Decoding secrets where timing side channels matter (for example PEM private keys): a constant-time decoder was requested and closed without one (#426), and the lookup and compaction paths depend on the data.
- Short, whitespace-heavy inputs through base64_to_binary_safe (the README says a few dozen characters with 5% whitespace can be nearly 3x slower), or through atomic_base64_to_binary_safe, which is 1.5–1.8x slower at every size.

## How it is fast

The decoder works on 64-character blocks. vpshufb/vqtbl nibble lookups (aqrit's delta/check tables) classify each byte as a base64 digit, ASCII whitespace or garbage, giving 64-bit whitespace and error masks. A block with no whitespace is translated and packed straight to 48 bytes, and long clean inputs take a two-block fast path. A block with whitespace is compacted (animetosho-style pshufb stream compaction on SSE/AVX2/NEON, vpcompressb on AVX-512 VBMI2) into a 384-byte stack buffer that is decoded in 64-byte groups, so sparse newlines never drop the loop to scalar code. The encoder uses Muła's pshufb lookup and inserts line feeds in-register. The best kernel is chosen at runtime (SSE/Westmere, AVX2/Haswell, AVX-512/Ice Lake on x86), and there are separate NEON, RVV, LoongArch LSX/LASX and POWER source files.

## Compared with alternatives

Pick simdutf over aklomp/base64, Turbo-Base64 or lemire's fastbase64 when the input can contain whitespace or needs base64url, strict/loose padding control, or JavaScript-compatible semantics; aklomp/base64 rejects any non-alphabet byte and supports only '+/'. Stay with aklomp/base64 for a small C99 dependency on clean input, or Turbo-Base64 for raw speed on short clean strings when GPL-3.0 is acceptable. No library-level head-to-head against either has been published; simdutf's benchmark_base64 includes libbase64, but the README gives no results.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib via CMake, or source-drop (single-header amalgamation: simdutf.h + simdutf.cpp, optionally base64-only) |
| **Dependencies** | none (Python 3 only to regenerate the amalgamation; can even build without libstdc++ via SIMDUTF_NO_LIBCXX, experimental) |
| **Minimum toolchain** | C++17 with GCC, Clang or MSVC (GCC on Windows unsupported); CMake 3.18+; the AVX-512 kernels need GCC 8+, Clang 6+ or VS 2022 plus binutils 2.30+; the C API needs C11; the compile-time _base64 literal needs C++23 |
| **Platforms** | x86-64 with runtime dispatch (SSE, AVX2, AVX-512 with VBMI2 on Ice Lake/Zen 4+), AArch64 NEON, RISC-V RVV (only when compiled with -march=rv64gcv), LoongArch LSX/LASX (LASX dispatch only with GCC 15+), POWER, and a scalar fallback everywhere else |
| **Thread safety** | Documented. Functions are reentrant and single-threaded, and CPU detection on first use is thread-safe (function-local statics). The dispatch objects are globals that may be destroyed when the main thread exits, so threads still calling during shutdown can break. atomic_base64_to_binary_safe exists for output buffers that other threads may read concurrently. |
| **Drop-in for the baseline** | partial — the fastbase64 and fastbase64.coreutils CLIs aim to be drop-in replacements for BSD and GNU base64. The library API is its own: caller-sized buffers, a result struct, and more lenient decoding by default than RFC 4648 decoders. |

## Gotchas

- base64_to_binary and base64_to_binary_details do not check bounds. The output must be at least maximal_binary_length_from_base64() bytes (or binary_length_from_base64() when the input has whitespace), or the docs warn of a buffer overflow; use base64_to_binary_safe when capacity is fixed.
- result.count means different things depending on the function: base64_to_binary gives the error position or the bytes written, _safe gives the input consumed with the output length returned by reference, and _details returns both. On error, the fast paths may not have decoded everything before the bad character unless you pass decode_up_to_bad_char=true, which is slower (#847, open).
- The \*_accept_garbage options silently skip non-alphabet bytes and stop at the first '='.
- There is no streaming state object. Chunked encoding must feed multiples of 3 bytes, and chunked decoding carries the unconsumed tail over with stop_before_partial; tools/fastbase64.cpp is the reference pattern.

## Known shortcomings

- Base64 speed evidence is first-party only (README performance table; ratios derived: \~27x on M4 Max, \~3.5x on Xeon 6548N for 100 MB decode); the Authorea base64 paper could not be retrieved.
- The only first-party base64 numbers come from a CLI script whose timings include python3 start-up, so the 1 MB rows are mostly noise; no compiler or flags, and the Linux comparison is not like-for-like (GNU base64 decodes its own 76-column wrapped output). No library-level head-to-head published. Default decoding is loose (missing padding and extra bits accepted; strict is opt-in); the fast decode path is not bounds-checked; no constant-time decode (#426). Widely deployed: V8's Uint8Array base64 calls simdutf.

## Caveats and trade-offs

The Authorea preprint 'Base64 Decoding with Ignorable Characters using SIMD instructions' (Lemire, 2025; DOI 10.22541/au.175692137.72576748/v1, with an earlier v1 at 10.22541/au.173866897.72952916/v1) is not peer-reviewed and its full text is behind a bot check. It is not on arXiv or HAL, so none of its numbers were verified. The replacement numbers are end-to-end CLI timings that include process startup and I/O, with no compiler or flags stated. On Linux the decode comparison is not like-for-like: GNU base64 decodes its own 76-column line-wrapped output while fastbase64 decodes its own unwrapped output. The repo is dual-licensed Apache-2.0 or MIT; the code under benchmarks/competition is 'for research purposes only' and is not part of the library.

C++17 library; base64 feature can be compiled out (--with-base64); safe variants have measurable overhead on whitespace-heavy short inputs per the project's own README

## Maintenance

Very active: release v9.2.1 on 2026-09-23, commits the same day as this review, a fuzzing setup, and 54 open issues. Dual Apache-2.0/MIT and embedded in Node.js, V8/Chromium, Bun, Cloudflare workerd and others, so the base64 path gets heavy production use. Only benchmarks/competition is research-only code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The paper DOI returns 403 (bot check) through both curl and WebFetch; its Crossref abstract says only 'multiply', gives no numbers, and it is an unreviewed Authorea preprint. The simdutf README fastbase64 Performance section does give first-party numbers against the system base64 tool, with CPU models and a public script (scripts/base64bench.sh), but no compiler or flags, so tier C.
- **Verifier notes:** The paper could not be fetched (Authorea 403 through curl and WebFetch), so I replaced benchmark_url with the README fastbase64 Performance section, which has verifiable numbers and CPU models; the tier stays C. simdutf appears in known_list.txt only because wave 7 merged it, so it is not a pre-existing duplicate. The license is dual (Apache-2.0 OR MIT), not Apache-2.0 alone.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `license`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** Lemire browser test (Apple M4): Chrome (simdutf) 19 / 4.6 GB/s vs older Firefox 0.34 / 0.40 GB/s.
- **Pages the verifier opened:**
  - <https://github.com/simdutf/simdutf>
  - <https://github.com/simdutf/simdutf#readme>
  - <https://github.com/simdutf/simdutf/blob/master/scripts/base64bench.sh>
  - <https://api.crossref.org/works/10.22541/au.175692137.72576748/v1>
  - <https://www.authorea.com/doi/pdf/10.22541/au.175692137.72576748/v1>
  - <https://www.authorea.com/doi/full/10.22541/au.175692137.72576748/v1>
  - <https://export.arxiv.org/api/query?search_query=all:base64+AND+au:lemire&max_results=10>
  - <https://github.com/lemire/base64data>
  - <https://github.com/lemire/base64scale>
  - <https://lemire.me/blog/?s=base64+spaces>
- **Sources the enricher read:**
  - <https://github.com/simdutf/simdutf>
  - <https://github.com/simdutf/simdutf#readme>
  - <https://github.com/simdutf/simdutf#performance>
  - <https://github.com/simdutf/simdutf/blob/master/scripts/base64bench.sh>
  - <https://github.com/simdutf/simdutf/blob/master/tools/fastbase64.cpp>
  - <https://github.com/simdutf/simdutf/blob/master/src/generic/base64.h>
  - <https://github.com/simdutf/simdutf/blob/master/src/haswell/avx2_base64.cpp>
  - <https://github.com/simdutf/simdutf/blob/master/src/icelake/icelake_base64.inl.cpp>
  - <https://github.com/simdutf/simdutf/blob/master/src/arm64/arm_base64.cpp>
  - <https://github.com/simdutf/simdutf/blob/master/src/westmere/sse_base64.cpp>
  - <https://github.com/simdutf/simdutf/blob/master/src/rvv/rvv_base64.cpp>
  - <https://github.com/simdutf/simdutf/blob/master/include/simdutf/base64_implementation.h>
  - <https://github.com/simdutf/simdutf/blob/master/include/simdutf/scalar/base64.h>
  - <https://github.com/simdutf/simdutf/blob/master/include/simdutf_c.h>
  - <https://github.com/simdutf/simdutf/blob/master/benchmarks/base64/benchmark_base64.cpp>
  - <https://github.com/simdutf/simdutf/releases>
  - <https://github.com/simdutf/simdutf/issues?q=base64>
  - <https://github.com/simdutf/simdutf/issues/380>
  - <https://github.com/simdutf/simdutf/issues/426>
  - <https://github.com/simdutf/simdutf/issues/763>
  - <https://github.com/simdutf/simdutf/issues/847>
  - <https://github.com/simdutf/simdutf/issues/908>
  - <https://github.com/lemire/base64scale>
  - <https://github.com/v8/v8/blob/main/src/builtins/builtins-typed-array.cc>
  - <https://lemire.me/blog/2025/11/29/how-fast-can-browsers-process-base64-data/>
  - <https://hn.algolia.com/api/v1/search?query=simdutf%20base64>
  - <https://hn.algolia.com/api/v1/search?query=lemire.me%20base64>
  - <https://github.com/aklomp/base64>
  - <https://github.com/powturbo/Turbo-Base64>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/simdutf/simdutf`) · [data/wave7/enrich/raw/github_com_simdutf_simdutf.json](../../../data/wave7/enrich/raw/github_com_simdutf_simdutf.json) (enrichment confidence 0.75)

</details>
