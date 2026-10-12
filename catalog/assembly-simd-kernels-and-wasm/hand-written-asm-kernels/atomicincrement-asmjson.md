# asmjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust crate with hand-written x86-64 AVX-512BW assembly` · `MIT` · 🟢 active

> Experimental Rust JSON parser with a hand-written AVX-512BW assembly inner loop; about 1.6x sonic-rs on string-heavy synthetic JSON.

| | |
|---|---|
| **Beats** | sonic-rs (AVX2 lazy Value), simd-json and serde_json |
| **Claimed result** | String array: asmjson/sax 10.78 GiB/s and asmjson/dom 10.93 GiB/s vs sonic-rs 6.92 GiB/s (1.56x and 1.58x, derived), serde_json 2.41, simd-json 1.91 GiB/s; string object: sax 8.29 vs sonic-rs 4.06 GiB/s (2.0x, derived); mixed: sax 1.17 GiB/s vs sonic-rs 478 MiB/s (2.5x, derived). |
| **Workload** | cargo bench on a single core over 10 MiB of synthetic JSON: string array, string object and mixed documents. |
| **Metric** | throughput |
| **Hardware** | Not stated for the main table (an example names a Ryzen 9 9955HX); needs Ice Lake or later Intel or Zen 4 or later AMD for AVX-512BW |
| **Compiler and flags** | cargo bench with criterion 0.5 (benches/parse.rs); .cargo/config.toml sets rustflags -C target-cpu=native; bench profile adds debug=1; rustc version not stated |
| **Adoption** | 6 stars, 0 forks; crates.io 550 downloads (229 recent), latest version 0.2.6 |
| **Last commit** | 2026-04-09 |
| **Links** | [repository](https://github.com/atomicincrement/asmjson) · [benchmark](https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/README.md) |

## Verdict

The author's criterion runs used one core of an AMD Ryzen 9 9955HX (Zen 5; the CPU is named only in doc/paper/paper.md, not the README), RUSTFLAGS -C target-cpu=native and an unstated rustc, on 10 MiB of synthetic escape-free JSON with string and key lengths summed after parsing. On a string array asmjson/sax reached 10.78 and asmjson/dom 10.93 GiB/s versus sonic-rs 6.92 GiB/s (about 1.6x); on a string object 8.29 versus 4.06 GiB/s; on mixed records 1.17 GiB/s versus 478 MiB/s, a lead that excludes the number conversion the baselines perform.

## Use it when

- Large string-heavy JSON (logs, JSON Lines, tokenizer or config dumps) on Zen 4/Zen 5 or Ice Lake+ servers, where you read strings and keys and rarely need numeric values.
- Single-pass SAX extraction (counting, filtering keys, copying string spans) with no per-document tape allocation.
- Parallel parsing of mmapped JSON Lines with Rayon: the author's mmap_parallel example reports 26.6 GiB/s on a 1 GiB file.
- Research or teaching on bit-parallel JSON classification (AVX-512BW mask registers versus u64 SWAR) in Rust.

## Skip it when

- Production or untrusted input: the README says experimental and not production ready, the assembly is unaudited for adversarial input, and two hot-path string-scanning bugs were fixed only in April 2026.
- When you need strict RFC 8259 validation: it accepts every control byte below 0x20 as whitespace and does not reject unescaped control characters inside strings.
- Number-heavy documents whose values you will actually read: numbers stay as text until as_i64/as_f64 is called, so the published mixed-workload lead (which never converts a number) overstates the end-to-end gain.
- Nesting deeper than 64 levels (MAX_JSON_DEPTH = 64), or frequent keyed lookups: get(key) walks the object linearly.
- C++ projects (Rust crate only; the assembly entry points are internal and there is no C header, so use simdjson or sonic-cpp), and non-Linux x86-64 targets (see gotchas).

## How it is fast

Each step loads 64 input bytes and classifies them with AVX-512BW compares into mask registers: whitespace (any byte at or below 0x20), quote, backslash, comma, '}' and ']'. tzcnt over those masks then skips whole whitespace runs and string bodies at once, and the tail uses a masked load, so nothing is read past the input. The state machine is direct-threaded assembly that writes tape entries straight into a pre-sized Vec (or calls the SAX vtable). Strings and numbers are recorded as borrowed source slices, with unescaping only when escapes are present and no numeric conversion at parse time; short integers are validated with a SWAR digit test. The portable path does the same 64-byte classification with u64 SWAR bit tricks.

## Compared with alternatives

None of the hand-written-assembly siblings is a JSON parser. Against the catalogued JSON parsers, pick asmjson only for Rust on AVX-512BW hardware with string-heavy input where you accept lax validation. Prefer sonic-rs (catalogued, wave 4) or serde_json for robust Rust parsing, and simdjson or yyjson from C++.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none at runtime (serde optional via the 'serde' feature); build-dependency cc assembles asm/x86_64/parse_json_zmm_sax.S and parse_json_zmm_dom.S on every x86_64 target |
| **Minimum toolchain** | Rust edition 2024 (rustc 1.85+); a C toolchain whose assembler accepts GNU Intel-syntax ELF .S files on x86_64 |
| **Platforms** | x86-64 Linux with AVX-512BW for the assembly path (Ice Lake+ or Zen 4+); the portable SWAR path compiles on any target; CI runs only cargo test on ubuntu-latest, so x86-64 macOS and Windows are untested |
| **Thread safety** | Parsers are reentrant free functions; Dom borrows the source string; DomEntry has unsafe impl Send and Sync over its raw pointer. Concurrency is otherwise not documented. |
| **Drop-in for the baseline** | false — own tape/SAX API rather than a Value tree or serde_json::from_str; the serde feature deserializes from the tape via from_taperef |

## Gotchas

- The README and JOSS-draft table (single core, 10 MiB synthetic JSON) was measured at commit 855c37c, before later assembly changes: the SAX escape-path fixes (f6bd9f4, 2026-03-17), the raw-escaped-string SAX contract (9c2d164), the carry-free eq_byte fix in the SWAR classifier (e77a521, 2026-04-09; the old has-zero-byte trick reported a quote followed by '#' as a closing quote and failed on a real 6 MB tokenizer.json) and the backslash-parity rewrite of both .S files (7d3c7a1, 2026-04-09). Before that rewrite, a string ending in an escaped backslash such as "a\\" was mis-scanned and rejected, and the rewrite adds a parity byte check to every string close in the hot loop. None of the numbers were re-run after these changes.
- The benchmark's 'full traversal' only sums string and key lengths. asmjson/sax and asmjson/dom never convert a number, while sonic-rs, serde_json and simd-json parse every number into i64/u64/f64 while building their Value, so the 2.5x (sax) and 1.9x (dom) mixed-workload leads include skipped work. The string_object document is one object with about 102,800 members whose keys repeat after key99999, so serde_json pays for BTreeMap inserts and deduplication. simd-json also clones the 10 MiB input on every iteration.
- The author's own log (doc/conversation.md) shows the sonic-rs string-array figure moving from 11.0 GiB/s (session 13, ahead of asmjson's 8.36) to 7.37 and then 6.92 GiB/s in later runs, with no recorded explanation. On mixed data the two were tied in session 18 (370 vs 368 MiB/s). The 1.6x headline depends on which run is quoted.
- The DOM path reserves src.len()/4 tape entries of 16 bytes (about 4x the input size) unless you pass a capacity, and re-parses from scratch with doubled capacity on overflow. The .S files use ELF-only directives (.type @function, .section .rodata) and System V argument registers, yet build.rs assembles them for every x86_64 target. The unsafe \*_zmm entry points raise SIGILL on CPUs without AVX-512BW.

## Known shortcomings

- No CPU for the main table, which dates from 2026-03-16 and predates the asm fixes of 2026-03-17 and 2026-04-09; the SAX path skips number conversion and validates loosely; Rust only.
- Enricher: numbers measured at commit 855c37c before the backslash-parity rewrite (7d3c7a1) and the eq_byte fix (e77a521) and never re-run; neither the asmjson sax nor dom path converts numbers while the baselines do, so the 2.5x/1.9x include skipped work; the author's log shows sonic-rs at 11.0, 7.37 and 6.92 GiB/s across runs; CPU named in doc/paper/paper.md (Ryzen 9 9955HX, Zen 5); sonic-rs is catalogued (wave 4).

## Caveats and trade-offs

Rust crate with hand-written AVX-512BW assembly, not directly usable from C++; baselines are Rust parsers (sonic-rs, serde_json, simd-json), and no C++ parser such as simdjson is compared. The README benchmark table was last refreshed on 2026-03-16, before 'fix: two bugs in SAX assembly escape path' (2026-03-17) and 'Fix assembly backslash-parity bug' plus a carry-free eq_byte fix for false-positive quote detection (2026-04-09); the synthetic data has no escapes, so the effect is probably small, but the numbers were measured on code later fixed for correctness bugs. The asmjson/sax path's number callback receives only the raw slice (no numeric conversion) while sonic-rs, serde_json and simd-json build Values with parsed numbers, which inflates the mixed-workload lead (2.5x). asmjson treats every byte below 0x20 as whitespace and does not reject control characters inside strings, so it validates less than the baselines. The simd-json row includes a Vec clone of the 10 MiB input each iteration. Synthetic documents only; CPU unstated for the main table (only the serde example names a Ryzen 9 9955HX). README labels it experimental and not production ready.

Requires AVX-512BW (a portable SWAR fallback exists); Rust API only, no C ABI documented; README labels it experimental and not production ready.

## Maintenance

Active through 2026-04-09 (v0.2.6, MIT, 6 stars, 550 crates.io downloads, no issues filed) but self-described as experimental. The published numbers predate the April 2026 assembly correctness fixes, so treat it as a research crate, not a serde_json or sonic-rs replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party criterion benchmark (benches/parse.rs, rustflags -C target-cpu=native in .cargo/config.toml) is public, but the README never names the CPU for the main table and the table (last refreshed 2026-03-16) predates assembly correctness fixes on 2026-03-17 and 2026-04-09, so it cannot reach A.
- **Verifier notes:** README numbers match the record (string array sax 10.78 / dom 10.93 vs sonic-rs 6.92 GiB/s; string object 8.29 vs 4.06; mixed 1.17 GiB/s vs 478 MiB/s), ratios correctly marked derived. Tier C stands on two grounds: no CPU model for the main table, and the numbers predate hot-path assembly correctness fixes; also record the SAX no-number-conversion and lax-validation asymmetries as shortcomings. Metadata confirmed: MIT, last commit 2026-04-09, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-30 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/README.md>
  - <https://github.com/atomicincrement/asmjson>
  - <https://github.com/atomicincrement/asmjson/commits>
  - <https://github.com/atomicincrement/asmjson/commits/master/README.md>
  - <https://github.com/atomicincrement/asmjson/commits/master/asm>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/benches/parse.rs>
  - <https://crates.io/api/v1/crates/asmjson>
- **Sources the enricher read:**
  - <https://github.com/atomicincrement/asmjson>
  - <https://github.com/atomicincrement/asmjson/commits>
  - <https://github.com/atomicincrement/asmjson/tree/master/src>
  - <https://github.com/atomicincrement/asmjson/tree/master/doc>
  - <https://github.com/atomicincrement/asmjson/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/README.md>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/benches/parse.rs>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/build.rs>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/src/sax.rs>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/src/dom/mod.rs>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/asm/x86_64/parse_json_zmm_sax.S>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/asm/x86_64/parse_json_zmm_dom.S>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/doc/conversation.md>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/doc/dev.md>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/doc/paper/paper.md>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/atomicincrement/asmjson/HEAD/.github/workflows/ci.yml>
  - <https://crates.io/api/v1/crates/asmjson>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/atomicincrement/asmjson`) · [data/wave13/enrich/raw/github_com_atomicincrement_asmjson.json](../../../data/wave13/enrich/raw/github_com_atomicincrement_asmjson.json) (enrichment confidence 0.8)

</details>
