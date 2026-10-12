# base64-simd (Nugine/simd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust SIMD base64 (plus hex, base32, UUID) crate; made uutils base64 1.56x faster than GNU coreutils base64 end to end.

| | |
|---|---|
| **Beats** | GNU coreutils base64 (/usr/bin/base64, C), via the uutils coreutils base64 command that adopted base64-simd |
| **Claimed result** | uutils coreutils base64 with base64-simd 3.146 s +/- 0.037 vs /usr/bin/base64 4.901 s +/- 0.054, 1.56 +/- 0.02 times faster; vs the previous uutils build 5.998 s +/- 0.055, 1.91 +/- 0.03 times faster; user CPU 1.208 s vs 3.904 s for GNU (derived from page data: about 3.2x less user time), system time 1.937 s vs 0.996 s. |
| **Workload** | Encode a single-line 4 GB file (/tmp/oneline_4G.txt) with the uutils coreutils base64 applet built on base64-simd versus /usr/bin/base64 and the previous uutils build, hyperfine -N --warmup 3, 10 runs. |
| **Metric** | throughput |
| **Compiler and flags** | uutils built with ./target/release/coreutils (cargo release profile of the coreutils workspace); GNU base64 version and build flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | SIMD-accelerated encode/decode: the README says the crates select SIMD functions automatically when available and cites Wojciech Mula's 0x80.pl base64 articles as the algorithm source; GNU base64 uses a scalar gnulib routine (my inference, not stated on the page). |
| **Adoption** | 268 stars; base64-simd crate 164,897,007 downloads on crates.io; used by uutils coreutils (uucore features 'encoding' and 'checksum') |
| **Last commit** | 2026-08-30 |
| **Links** | [repository](https://github.com/Nugine/simd) · [benchmark](https://github.com/uutils/coreutils/pull/8578) |

## Verdict

A uutils maintainer (PR #8578, 2025-09-08) used hyperfine -N --warmup 3 (10 runs) to encode a 4 GB single-line file of 'A' characters with the uutils base64 command built on base64-simd 0.8: 3.146 s, against 4.901 s for /usr/bin/base64 (GNU coreutils, version and flags not stated) and 5.998 s for the previous uutils build, which is 1.56x and 1.91x faster; no CPU or compiler details were given.

## Use it when

- Rust programs that encode or decode large base64 payloads (MIME bodies, data URLs, JSON blobs, CLI tools) where the base64 crate or a scalar loop shows up in profiles.
- x86-64 with SSSE3 or AVX2, aarch64 with NEON, or wasm32 with simd128, where the crate's vector paths exist.
- Validation-heavy paths: check() verifies base64 without writing output, and decode_inplace avoids a second buffer.
- Browser-compatible decoding: the forgiving_decode functions implement the WHATWG forgiving-base64 rules.
- no_std targets: the crate builds without std or alloc (runtime CPU detection then needs compile-time target features instead).

## Skip it when

- When you want the fastest base64 available: there is no AVX-512 (VBMI) path (issue #67 open since April 2026), while C libraries such as aklomp/base64, simdutf and Turbo-Base64 ship AVX-512 kernels; no head-to-head against them was found.
- When you need line wrapping (76-column MIME, GNU base64 default) built in: the crate emits one unwrapped string, and the caller must insert newlines.
- When you need fixes from the repository: the crates.io release is still 0.8.0 from 2022-12-28, and every later commit (dev version 0.9.0-dev, MSRV 1.85) is unreleased.
- On CPUs without SSSE3 (old x86) or on other architectures (POWER, RISC-V, s390x), where it falls back to scalar code and loses its edge.
- Projects that audit unsafe code strictly: the README says the project 'relies heavily on unsafe code'.

## How it is fast

Encoding loads 24 input bytes into a 256-bit register (12 into 128-bit), splits them into 6-bit fields with shuffles and multiply-shift tricks, and maps the values to ASCII with a pshufb offset lookup table, following Wojciech Mula's 0x80.pl SIMD base64 algorithm; decoding and validation use aqrit's 'alsw' lookup scheme. The vsimd dispatch macro picks AVX2, SSSE3, NEON or WASM simd128 at runtime (feature 'detect', via std::arch feature detection) or at compile time when the target already enables AVX2/NEON/simd128, with a scalar fallback. The GNU baseline uses a scalar gnulib table loop, so the measured gain is SIMD against scalar code, not a language effect.

## Compared with alternatives

Pick it when your Rust code needs a base64 or hex codec; the uutils coreutils sibling is the CLI that embeds this crate, and the other string-and-text siblings (regex, mail-parser, sd, tuc) solve different problems.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | outref and vsimd (same repo); rayon only with the 'parallel' feature (which also needs 'unstable', i.e. nightly) |
| **Minimum toolchain** | Rust 1.63 for the published 0.8.0 (crates.io rust_version); repository HEAD declares rust-version 1.85.0 |
| **Platforms** | x86/x86-64 (SSSE3, AVX2), aarch64 (NEON), armv7 NEON with 'unstable', wasm32 simd128; scalar fallback elsewhere |
| **Thread safety** | Stateless functions on const config values; runtime detection uses std's cached feature checks, so calls are safe from any thread (no shared mutable state in the API). |
| **Drop-in for the baseline** | partial — it replaces a base64 encode/decode routine inside a program; it is not a replacement for the GNU base64 command, which uutils wraps around it |

## Gotchas

- The 1.56x figure is the uutils base64 command, not the crate: uutils calls STANDARD.encode_to_string per chunk and then copies the String into a VecDeque (src/uucore/src/lib/features/encoding.rs), and its system time (1.937 s) is double GNU's (0.996 s), so the number mixes the crate with the uutils I/O path and understates the encoder alone.
- The benchmark input is a 4 GB file containing only the letter 'A' (per the reporter in uutils issue #8574), timed on an undisclosed machine; on the reporter's i7-13620H GNU base64 took 2.461 s, half the 4.901 s the maintainer measured for GNU, and no post-fix run exists on that machine.
- Open issue #78 (July 2026): building with -C target-cpu=x86-64-v2 makes unicode-simd's UTF-16/UTF-32 swap hit unreachable!() on SSSE3-only CPUs because the SSSE3 dispatch arm is not treated as SSE4.1; it shows the dispatch tables can be wrong for intermediate ISA levels, though base64-simd itself was not reported.
- Open issue #43: a Rust 1.75 regression where LLVM stopped emitting vpavgb for _mm256_avg_epu8 (upstream stdarch #1477) slowed vsimd code; performance depends on the rustc version.

## Known shortcomings

- Only evidence is one maintainer comment in uutils PR #8578 (1.56x vs GNU base64, 1.91x vs old uutils) with no CPU or GNU version; CLI timing includes I/O; no comparison with aklomp/base64 or Turbo-Base64; the crate is still 0.8.0 (2022-12-28).
- Enricher: the measured number is the uutils base64 command, not the crate (uutils calls encode_to_string per chunk and copies into a VecDeque); system time 1.937 s vs GNU 0.996 s; the input is 4 GB of the single byte 'A' (issue #8574); machine unstated, and the reporter's i7-13620H measured GNU at 2.461 s against the maintainer's 4.901 s. The measured code is crates.io 0.8.0 (2022-12-28); no AVX-512 path (#67); open #78 (unreachable!() with target-cpu=x86-64-v2) and #43 (Rust 1.75 vpavgb regression); the author opened #81 on 2026-10-08 to restore maintenance with AI assistance.

## Caveats and trade-offs

No comparison against aklomp/base64, Turbo-Base64 or fastbase64 was found. The project's own harness (Nugine/simd-benches) compares base64-simd only against Rust crates, and its published results live on a github.io page that is blocked here. The only C-baseline number is a maintainer's PR comment (uutils/coreutils #8578, 2025-09-08, merged 2025-09-09) with no machine description, no GNU coreutils version and no build flags; the end-to-end CLI time also includes the uutils I/O path (system time 1.937 s against GNU's 0.996 s), so 1.56x understates the encoder gap, while the 1.91x gain over the previous uutils build is a before/after on the same program. GNU base64 is not in the listed baselines (aklomp/base64, Turbo-Base64, fastbase64). The published base64-simd crate is still 0.8.0 (released 2022-12-28); repository commits after that (last 2026-08-30) are not in a crates.io release. [retier] Enricher: the measured figure is the uutils base64 command (per-chunk encode_to_string plus a VecDeque copy) on 4 GB of the byte 'A', machine unstated; measured code is crates.io 0.8.0; open #78 (unreachable!() with target-cpu=x86-64-v2) and #43.

Part of the Nugine/simd monorepo (base64-simd, hex-simd, base32-simd, unicode-simd, uuid-simd, vsimd); SIMD paths are chosen at compile time or by runtime detection ('detect' feature) with a fast fallback. The latest crates.io release (0.8.0) dates from 2022-12-28 while the repo was committed to as late as 2026-08-30.

## Maintenance

MIT-licensed and very widely used (about 165 million crates.io downloads), but in maintenance mode: no crates.io release since 0.8.0 (2022-12-28), commits since then are CI and dependency fixes (last 2026-08-30), and the author opened issue #81 'Restore project maintenance with AI assistance' on 2026-10-08.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only C-baseline numbers are a uutils maintainer's hyperfine comment on PR #8578 (2025-09-08): 3.146 s vs /usr/bin/base64 4.901 s, 1.56x, and 1.91x over the previous uutils build; no CPU, compiler, GNU version or build flags are given, so it cannot be A, and it is a first-party measurement by the adopting project, not an independent suite.
- **Verifier notes:** PR #8578 hyperfine output matches the record exactly (4.901 s, 3.146 s, 5.998 s, 1.56 +/- 0.02 and 1.91 +/- 0.03 times faster); I did not see the hyperfine flags quoted, so the record's '-N --warmup 3, 10 runs' is unconfirmed. Shortcomings to record: single maintainer comment without hardware or GNU version, CLI-level comparison mixes in I/O, the win is SIMD versus GNU's scalar routine rather than a language effect, and the listed fast C base64 libraries were never compared.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-114 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/uutils/coreutils/pull/8578>
  - <https://github.com/Nugine/simd>
  - <https://github.com/Nugine/simd/commits>
  - <https://crates.io/api/v1/crates/base64-simd>
- **Sources the enricher read:**
  - <https://github.com/Nugine/simd>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/base64-simd/Cargo.toml>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/base64-simd/README.md>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/base64-simd/src/lib.rs>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/base64-simd/src/multiversion.rs>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/base64-simd/src/encode.rs>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/base64-simd/src/forgiving.rs>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/vsimd/src/isa.rs>
  - <https://raw.githubusercontent.com/Nugine/simd/HEAD/crates/vsimd/src/lib.rs>
  - <https://github.com/Nugine/simd/commits/main>
  - <https://github.com/Nugine/simd/issues?q=is%3Aissue>
  - <https://github.com/Nugine/simd/issues/78>
  - <https://github.com/Nugine/simd/issues/81>
  - <https://github.com/Nugine/simd/issues/43>
  - <https://github.com/Nugine/simd-benches>
  - <https://github.com/uutils/coreutils/pull/8578>
  - <https://github.com/uutils/coreutils/issues/8574>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uucore/Cargo.toml>
  - <https://raw.githubusercontent.com/uutils/coreutils/HEAD/src/uucore/src/lib/features/encoding.rs>
  - <https://crates.io/api/v1/crates/base64-simd>
  - <https://crates.io/api/v1/crates/base64-simd/reverse_dependencies>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/nugine/simd`) · [data/wave14/enrich/raw/github_com_nugine_simd.json](../../../data/wave14/enrich/raw/github_com_nugine_simd.json) (enrichment confidence 0.6)

</details>
