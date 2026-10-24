# sccache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Compiler-cache wrapper for C, C++, CUDA and Rust with local or cloud storage; skips recompiling unchanged units.

| | |
|---|---|
| **Beats** | uncached compile (no compiler cache) |
| **Claimed result** | Cargo build step 17 min 26 s uncached, 6 min 23 s on the first sccache run (C/C++ 1,803 hits and 319 misses, 85 percent; Rust 10 hits and 223 misses, 4 percent) and 2 min 46 s on the rerun; whole Lint and Format job 1,425 s uncached versus 711 s and 478 s. About 2.7x then 6.3x on the cargo build step (derived from page data). |
| **Workload** | CI lint job of the amplihack-rs repository: cargo build (dev profile) that also compiles the C/C++ library lbug through cmake, run uncached on main, then with sccache on first and repeated runs, using GitHub Actions cache storage. |
| **Metric** | build-time |
| **Compiler and flags** | cargo build, dev profile; C/C++ built through cmake (compiler version not stated) |
| **Adoption** | 7.8k stars; Mozilla project |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/mozilla/sccache) · [benchmark](https://github.com/rysweet/amplihack-rs/pull/1571) |

## Verdict

One third-party CI measurement (amplihack-rs PR #1571, merged 2026-10-16): a GitHub Actions dev-profile cargo build that also compiles the C++ library lbug through cmake took 17 min 26 s on an uncached main run, 6 min 23 s on the PR's first run with sccache and the GitHub Actions cache backend (C/C++ objects mostly already cached by main's clippy step: 1,803 hits, 319 misses; Rust 10 hits, 223 misses; 219 write errors), and 2 min 46 s on a rerun, about 2.7x and 6.3x (derived from page data). Runner hardware, compiler and sccache versions are not stated and the baseline is a different workflow run, though four other uncached main runs spent 763 to 1,062 s in the same doc-review step against 384 s and 168 s with sccache, so the gap exceeds run-to-run spread.

## Use it when

- Ephemeral CI runners with a shared remote cache (S3, GCS, Azure, Redis, GitHub Actions cache) where most C/C++ objects match what main already built, such as the amplihack-rs lint job whose first sccache run hit 85% of C/C++ compiles.
- Mixed Rust and C/C++ projects (cmake- or cc-built native dependencies under cargo) that want one cache for rustc and the C/C++ compiler.
- CUDA or HIP code built with nvcc, clang or hipcc, which sccache caches alongside C/C++ and Rust.
- Windows MSVC builds that can use /Z7 (CMake 3.25+ with CMAKE_MSVC_DEBUG_INFORMATION_FORMAT=Embedded and CMP0141 NEW), as a maintained replacement for clcache.
- Teams that want distributed compilation with authentication, TLS and sandboxed build servers on 64-bit Linux or FreeBSD, with Linux, Windows or macOS clients.

## Skip it when

- Local GCC/Clang builds where ccache is available: the only head-to-head (issue #160, 2017, Firefox, Clang 4.0) had fully cached sccache at 107 s wall against 35 s for ccache in direct mode; sccache gained a direct mode in 2023 and the issue was closed without new timings.
- Rust workspaces dominated by bin, dylib, cdylib or proc-macro crates, or incremental dev builds: these cannot be cached (the amplihack-rs first run hit only 4% of Rust compiles).
- MSVC projects that rely on precompiled headers (/Yc, /Fp) or a shared /Zi PDB: those invocations are marked not cacheable and go to the compiler.
- Large GitHub Actions matrices writing concurrently to the GitHub Actions cache: HTTP 429 throttling silently drops writes with no retry (open issue #2821 reports 45-90% write loss with five concurrent writers).
- Several sccache servers sharing one local cache directory: the local backend supports only a single server and concurrent servers race and cause spurious build failures.

## How it is fast

Content-addressed result caching: for C/C++ the key is a BLAKE3 digest of the preprocessed source plus the compiler binary hash, language, preprocessor and architecture arguments and environment; for Rust it hashes the source, rustc and sysroot libraries, and the parsed arguments. A hit downloads or copies the stored object instead of compiling, so a shared remote cache lets ephemeral CI runners reuse objects built by earlier jobs. A 'preprocessor cache mode' (ccache's direct mode, added in PR #1882 in 2023 and on by default) records each source's include set so a hit can skip running the preprocessor, but only for GCC/Clang with local disk storage; MSVC and remote backends still preprocess on every lookup.

## Compared with alternatives

Pick sccache over clcache for any MSVC build that needs a maintained tool or remote storage, and over distcc or icecream when you want cached results reused across machines and runs rather than only farming out compiles (sccache-dist also covers distribution, with authentication). For local-only GCC/Clang builds the catalog has no evidence that it beats ccache.

## Integration

| | |
|---|---|
| **Form** | standalone executable (Rust crate; prebuilt x86-64 binaries, package managers, cargo install, or the mozilla-actions/sccache-action GitHub Action) |
| **Dependencies** | none at runtime for the client; optional storage service (S3, GCS, Azure, Redis, Memcached, WebDAV, GHA cache); OpenSSL for the dist-server feature (can be vendored); bubblewrap or Docker on distributed build servers |
| **Minimum toolchain** | Building sccache needs Rust 1.91.0 (rust-version in Cargo.toml at version 0.19.0); cargo 1.40+ for rustc-wrapper; CMake 3.4+ for compiler launchers, and CMake 3.25+ with CMP0141 for MSVC embedded debug info |
| **Platforms** | Prebuilt x86-64 binaries for Linux (musl), Windows and macOS, other targets via cargo; distributed build servers must be 64-bit Linux or FreeBSD |
| **Thread safety** | One local server handles concurrent compile requests from parallel builds and integrates with the GNU make jobserver; a local disk cache supports only one server at a time. |
| **Drop-in for the baseline** | partial — wraps the existing compiler without build changes, but MSVC needs /Z7 instead of /Zi, and PCH, shared PDBs, non-lib Rust crates, incremental Rust and GCC/MSVC C++20 modules bypass the cache |

## Gotchas

- Absolute paths must match for a hit unless SCCACHE_BASEDIRS is set, so CI jobs with different checkout paths miss each other's entries by default.
- Preprocessor cache mode can return stale objects when a header that would have been included did not exist at caching time and appears later, or when ignore_time_macros is on; it turns itself off for sources containing __DATE__, __TIME__ or __TIMESTAMP__.
- If the client cannot reach its server the build fails by default; set SCCACHE_IGNORE_SERVER_IO_ERROR=1 to fall back to the real compiler.
- SCCACHE_C_CUSTOM_CACHE_BUSTER separates C/C++ caches between incompatible invocations, but there is no equivalent for Rust.

## Known shortcomings

- Only a third-party CI log (amplihack-rs PR 1571) against no cache, not against ccache; issue 160 has ccache faster on a cached Firefox build (35 s, 96 s without direct mode, vs 107 s); uncached runs vary.
- Enricher: cross-run comparison whose gap exceeds run spread, with step reordering in the same PR and hits inherited from clippy; no evidence sccache beats ccache; GitHub Actions backend drops writes on HTTP 429 (#2821); preprocessor cache mode excludes MSVC and remote backends.

## Caveats and trade-offs

Neither the sccache README nor docs carry timing numbers. The reachable figures are one third-party CI pull request (opened and merged 2026-10-16) with a mixed Rust plus C++ workload, no runner hardware, compiler or sccache version stated, 219 sccache write errors from GitHub cache throttling, and the uncached run being a different pipeline run than the cached ones; the gain comes mostly from C/C++ objects already cached on main. Against ccache, the only measurement found is the repo's own issue https://github.com/mozilla/sccache/issues/160 (2017, Firefox clobber build with Clang 4.0.0 on Ubuntu 17.04, hardware not stated), where fully cached ccache took 35 s wall versus 107 s wall for sccache's local disk cache (3 to 4.5 times slower); the issue was closed in February 2024 as 'should be good now' without new measurements, so sccache has no evidence of beating ccache here. [verifier] In the same issue, ccache with compression = true and direct_mode = false took 96 s wall, so much of ccache's lead came from its direct mode. The PR's table also lists four other uncached main runs with doc-review steps of 763 to 1,062 s, so the uncached baseline varies run to run. [retier] Enricher: the cross-run gap exceeds the spread (four other uncached main runs spent 763-1,062 s in the doc-review step, against 384 s and 168 s with sccache), PR #1571 also moved the toolchain and rust-cache steps ahead of the measured build, and the 85% C/C++ hit rate came from objects main's clippy step had already cached. Preprocessor cache mode (PR #1882) works only with GCC/Clang on local disk, so MSVC and remote backends preprocess on every lookup; issue #160 (closed in 2024 without new timings) is the only ccache comparison, so there is no evidence sccache beats ccache. Open issue #2821: the GitHub Actions cache backend silently drops writes on HTTP 429 (45-90% loss with concurrent writers), matching the PR's 219 write errors. MSVC /Yc, /Fp and shared PDBs are not cacheable.

ccache-like wrapper with a client/server model and many storage backends (local disk, S3, GCS, Azure, Redis, Memcached, WebDAV, GitHub Actions cache); caches C, C++, CUDA and Rust; also offers icecream-style distributed compilation with authentication. Needs a background server process and cache storage configuration.

## Maintenance

Actively maintained Mozilla project (version 0.19.0 on main, 7.8k stars, Apache-2.0) with prebuilt binaries, so it can be adopted without building it; the GitHub Actions backend's dropped-write bug (#2821) and its retry PR (#2911) are still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** amplihack-rs PR #1571 lists cargo build 17 min 26 s uncached vs 6 min 23 s and 2 min 46 s with sccache (job 1,425 s vs 711 s and 478 s) from the CI jobs API, but runner hardware, compiler and sccache versions are unstated and runs are separate pipelines. Third-party CI anecdote without full methodology, so C.
- **Verifier notes:** All PR numbers and hit/miss stats match (17m26s, 6m23s, 2m46s; 1,425/711/478 s; 1,803/319 C/C++, 10/223 Rust; 219 write errors). Last commit 2026-10-24, Apache-2.0, 7.8k stars confirmed. Ratios are correctly marked derived.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-10 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/rysweet/amplihack-rs/pull/1571>
  - <https://github.com/mozilla/sccache>
  - <https://github.com/mozilla/sccache/commits/main>
  - <https://github.com/mozilla/sccache/issues/160>
- **Sources the enricher read:**
  - <https://github.com/mozilla/sccache>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/README.md>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/Cargo.toml>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/docs/Caching.md>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/docs/Local.md>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/docs/GHA.md>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/docs/Rust.md>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/docs/Architecture.md>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/docs/Distributed.md>
  - <https://raw.githubusercontent.com/mozilla/sccache/main/src/compiler/msvc.rs>
  - <https://github.com/mozilla/sccache/issues/160>
  - <https://github.com/mozilla/sccache/pull/1882>
  - <https://github.com/mozilla/sccache/issues?q=is%3Aissue+is%3Aopen+slow>
  - <https://github.com/mozilla/sccache/issues/2821>
  - <https://github.com/mozilla/sccache/issues/629>
  - <https://github.com/rysweet/amplihack-rs/pull/1571>
  - <https://github.com/rysweet/amplihack-rs/pull/1571/files>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/mozilla/sccache`) · [data/wave2/enrich/raw/github_com_mozilla_sccache.json](../../../data/wave2/enrich/raw/github_com_mozilla_sccache.json) (enrichment confidence 0.8)

</details>
