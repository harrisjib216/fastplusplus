# simdjson-oxcaml (simdjson-ox)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `OCaml (OxCaml)` · `MIT` · 🟢 active

> Native OxCaml simdjson port: reusable tape mode 1.18x RapidJSON geomean; DOM mode 0.69x RapidJSON, 4.9x Yojson.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | simdjson-ox-tape-reusable (reusable tape parser) geomean 1247.7 MB/s vs rapidjson-dom 1059.7 MB/s (\~1.18x, derived from page data; README states 118% of RapidJSON) and vs nlohmann-json-dom 132.2 MB/s (\~9.4x, derived from page data). Per fixture the tape-reusable mode beats RapidJSON on apache_builds (1555 vs 867 MB/s), citm_catalog (2072 vs 1649), gsoc-2018 (2257 vs 1092) and twitter (1428 vs 1048) but is slower on canada (759 vs 990), marine_ik (668 vs 885) and numbers (894 vs 1047). The recommended DOM API is slower than RapidJSON: simdjson-ox-reusable 729.5 MB/s and one-shot simdjson-ox 659.4 MB/s geomean (README: 69% of RapidJSON). Still behind C++ simdjson-dom (3344.5 MB/s) and sajson-dom (1650.9 MB/s). |
| **Workload** | Geometric-mean parse throughput (MB/s) across 7 standard JSON corpus fixtures (apache_builds, canada, citm_catalog, gsoc-2018, marine_ik, numbers, twitter.json), single P-core pinned, Bechamel/Google Benchmark harness |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-12700K (8 P-core + 4 E-core, 20 logical CPUs), pinned to logical CPU 0 (P-core) via taskset, performance governor, ASLR disabled, Fedora Linux 43, kernel 6.19.14-200.fc43.x86_64 |
| **Compiler and flags** | OCaml 'perf' dune profile (native flags -g, -gno-upstream-dwarf, -gdwarf-inlined-frames, -gdwarf-fidelity high) on OxCaml 5.2.0+ox / Dune 3.22.2; C++ comparators (RapidJSON, nlohmann, sajson, simdjson) built with GCC 15.2.1, CMake Release config |
| **Adoption** | 3 stars |
| **Last commit** | 2026-08-23 |
| **Links** | [repository](https://github.com/artempyanykh/simdjson-oxcaml) · [benchmark](https://github.com/artempyanykh/simdjson-oxcaml/blob/main/docs/parser-benchmark-snapshot-2026-08-15.md) |

## Verdict

The author ran one benchmark on 2026-08-15: an i7-12700K pinned to one P-core, with the OxCaml 5.2.0+ox perf profile against C++ parsers built by GCC 15.2.1 in CMake Release under Google Benchmark. On 7 simdjson-data fixtures, the reusable tape mode averaged 1,247.7 MB/s geomean against RapidJSON DOM's 1,059.7 MB/s (about 1.18x) and won 4 of 7. The recommended DOM API reached 729.5 MB/s (about 0.69x RapidJSON), and C++ simdjson reached 3,344.5 MB/s. RapidJSON was run with default parse flags and a fresh Document per iteration, and was built without RAPIDJSON_SSE2/SSE42 or -march flags.

## Use it when

- An OCaml service on x86-64 where Yojson or Jsont parsing is the bottleneck. On 100 KB-3 MB documents the DOM mode measured about 4.9x Yojson.Safe and 5.4x Jsont (geomean).
- Hot loops that parse many documents and can consume each result right away. The reusable `Tape.Parser` allocates nothing in steady state and was the fastest OCaml mode at 1,248 MB/s geomean.
- Object- and string-heavy JSON (API logs, catalogs, tweets). Tape mode beat RapidJSON on apache_builds, citm_catalog, gsoc-2018 and twitter.
- Teams already on OxCaml who want SIMD parsing without C++ FFI. The only C code is a tiny linker stub.

## Skip it when

- Stock OCaml. It needs the OxCaml 5.2.0+ox compiler and Jane Street's `ocaml_simd`, and will not build on upstream OCaml.
- ARM (Apple Silicon, Graviton). The SIMD code is x86 SSE only, there is no runtime CPU dispatch, and there is no AVX2 path yet.
- Float-heavy documents such as GeoJSON or numeric arrays, if you hoped to beat RapidJSON. Tape mode lost to it on canada, marine_ik and numbers. In the DOM path the author measured about 42% of cycles going to GC/promotion on canada.json.
- Cases that need error positions or messages, serialization, lazy On-Demand access, or exact integers beyond 63 bits.
- Untrusted or deeply nested input in production. The parser has no nesting-depth limit, it is a single-author project with 3 stars and no releases, and it has no issue history to learn from.

## How it is fast

Stage 1 follows simdjson's structural indexing on 64-byte blocks (four SSE 16-byte vectors): nibble lookup tables (PSHUFB) classify bytes, simdjson's backslash-run subtraction trick finds escapes, a carry-less-multiply prefix-XOR builds in-string masks, and the lookup-4 algorithm validates UTF-8. Structural positions stay compressed as one 64-bit mask per 64 input bytes, which stage 2, a tail-recursive descent, walks with count-trailing-zeros while writing either the `Json.t` tree or a tape whose strings share one byte buffer, so the reusable tape path allocates zero OCaml words per parse. Numbers use an 8-digit SWAR batch and a native port of Lemire's fast_float (Clinger fast path plus a 64x64-&gt;128 multiply lowered to one x86 `mul`), with a strtod fallback. OxCaml's unboxed `int64#`/`float#`, `[@zero_alloc]` checks and `[@@builtin]` popcnt/ctz intrinsics keep the hot loops free of boxing.

## Compared with alternatives

Pick it only when you must stay in OCaml/OxCaml with no C++ FFI. In the same run C++ simdjson was about 2.7x faster than its best mode and sajson about 1.3x faster. For C/C++, or where bindings are acceptable, simdjson or yyjson is the better choice. simd-json (Rust) and simdjson-go are the equivalent ports for other languages.

## Integration

| | |
|---|---|
| **Form** | module (dune library `simdjson`, built from source; no tags or releases, and the generated opam file still has placeholder homepage and dev-repo URLs, so expect to pin from git) |
| **Dependencies** | ocaml_simd (sse, avx, ppx, sexp sublibraries), janestreet_shims, base, stdlib_upstream_compatible, ppx_expect and ppx_template (preprocess); one C stub file |
| **Minimum toolchain** | OxCaml 5.2.0+ox (the setup script pins an OxCaml opam-repository commit), Dune 3.22 |
| **Platforms** | x86-64 only. It uses SSE 128-bit vectors with PSHUFB lookups and a carry-less multiply; the exact minimum ISA is not documented. No ARM, and no AVX2 dispatch yet. |
| **Thread safety** | Not documented. `Parser.t` and `Tape.Parser.t` own mutable buffers that are reused across calls, so use one per domain (inferred from the API). The one-shot `Simdjson.parse` creates its own buffers on every call. |
| **Drop-in for the baseline** | false. RapidJSON is a C++ library. Within OCaml the result is a new `Json.t` AST, not Yojson's polymorphic variants, and there is no printer. |

## Gotchas

- The tape returned by `Tape.Parser.parse` borrows the parser's buffers, in simdjson's `dom::parser` style. The next `parse` on that parser overwrites it. Use `Tape.parse` or `Tape.to_json` if you need to keep the result.
- Integers are 63-bit OCaml ints. Values beyond that but within the int64/uint64 range come back silently as `Float`, which loses precision. Larger integers are rejected as `Invalid_json`.
- Every parse failure is the single `Error Invalid_json`, with no position or category. Unimplemented paths and internal defects raise `Internal_error` instead. Stage 2 is recursive, and the design notes say pathologically nested input can overflow the native stack.
- Tape format limits: strings are capped at 16 MB (24-bit length), string offsets and container end indexes are 32-bit packed fields, and container element counts saturate at 24 bits.

## Known shortcomings

- The \~1.18x geomean win over RapidJSON comes only from the reusable tape mode, which still loses on canada, marine_ik and numbers; the recommended DOM API is slower than RapidJSON (729.5 vs 1059.7 MB/s geomean). The author notes the tape comparison is not strictly like-for-like, and the RapidJSON harness builds a fresh Document each iteration. Requires the OxCaml compiler.
- RapidJSON was built without -march or RAPIDJSON_SSE2/SSE42, so the 1.18x win is over a non-SIMD RapidJSON. 63-bit OCaml ints: larger int64/uint64 values silently become floats. Recursive stage 2 with no depth limit can overflow the native stack. Strings capped at 16 MB. x86-64 SSE only (no AVX2, runtime dispatch or ARM). Single author, 3 stars, no releases; errors carry no position.

## Caveats and trade-offs

The win over RapidJSON comes only from the lower-level tape mode with a reusable parser (zero OCaml allocation in the loop), while the RapidJSON harness builds a fresh rapidjson::Document every iteration. The author says tape vs DOM APIs 'are not identical enough for a strictly like-for-like comparison'. The recommended DOM API is about 0.69x RapidJSON, and tape mode loses to RapidJSON on 3 of 7 fixtures (canada, marine_ik, numbers). The author labels it a single-run, point-in-time snapshot (turbo on, frequency not locked). x86-only SIMD. Very new project with 3 stars.

Still \~2.7x slower than C++ simdjson-dom and \~1.3x slower than sajson-dom in the same run; OCaml GC allocates significant minor/major words per parse (reported in the table) unlike the zero/near-zero-alloc C++ parsers; SIMD path is currently x86-oriented (SSE/AVX via ocaml_simd), no ARM NEON yet; error reporting is described by the author as still rudimentary; only the 'tape-reusable' variant beats RapidJSON — the plain simdjson-ox and non-reusable tape variants sit at or below RapidJSON's geomean.

## Maintenance

Actively developed by a single author (last commit 2026-08-23) and MIT-licensed. It is usable today by pinning the git repo into an OxCaml switch, but it has no releases and the author describes the tape API as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (bench/parser_bench.ml orchestrating bench/parser_ocaml_bench.ml and bench/cpp/parser_cpp_bench.cpp, which runs RapidJSON/nlohmann/sajson/simdjson under Google Benchmark), and the snapshot page states compilers (OxCaml 5.2.0+ox, GCC 15.2.1), flags (OCaml perf profile -g/-gdwarf flags, C++ CMake Release) and CPU (i7-12700K, pinned P-core). All A criteria met.
- **Verifier notes:** Every number in the record matches the 2026-08-15 snapshot table and geomean ranking. Metadata checked via gh: MIT, 3 stars, not a fork, last commit 2026-08-23. The claim is accurate for the named tape-reusable variant, but the headline 'faster than RapidJSON' does not hold for the library's default DOM API. Corrections make that explicit.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/artempyanykh/simdjson-oxcaml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/docs/parser-benchmark-snapshot-2026-08-15.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/README.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/bench/dune>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/bench/cpp/CMakeLists.txt>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/bench/cpp/parser_cpp_bench.cpp>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/dune>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/dune-project>
- **Sources the enricher read:**
  - <https://github.com/artempyanykh/simdjson-oxcaml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/README.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/docs/parser-benchmark-snapshot-2026-08-15.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/simdjson.mli>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/parser.mli>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/parser.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/tape.mli>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/scanner.mli>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/scanner.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/simd_helpers.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/numeric_helpers.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/number_parsing.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/decimal_float.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/utf8_validator.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/string_parsing.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/parser_stubs.c>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/lib/dune>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/dune-project>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/simdjson.opam>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/.gitmodules>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/AGENTS.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/bench/cpp/parser_cpp_bench.cpp>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/bench/cpp/CMakeLists.txt>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/bench/parser_ocaml_bench.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/docs/parser-gc-investigation.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/docs/things-to-try.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/prd/tape-parser.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/prd/tape-performance-investigation.md>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/test/dom_unit_tests.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/blob/main/test/conformance_jsonchecker.ml>
  - <https://github.com/artempyanykh/simdjson-oxcaml/issues>
  - <https://github.com/artempyanykh/simdjson-oxcaml/commits/main>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/artempyanykh/simdjson-oxcaml`) · [data/wave4/enrich/raw/github_com_artempyanykh_simdjson_oxcaml.json](../../../data/wave4/enrich/raw/github_com_artempyanykh_simdjson_oxcaml.json) (enrichment confidence 0.85)

</details>
