# lo (just-js)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Small V8-based JavaScript runtime with C++ bindings; scores 1.09-1.41x Node 26 on the v8-v7 suite.

| | |
|---|---|
| **Beats** | Node.js (V8) |
| **Claimed result** | ahaoboy/js-engine-benchmark 2026-10-05 v8-v7 scores over Node 26.10.0; excluding Splay (where Node collapses to 15574 and 13056 on macOS and Windows against 35204 on ubuntu) lo leads by 1.09x on ubuntu, 1.26x on macOS arm64 and 1.01x on Windows (derived from page data). d8 beats lo on every platform. |
| **Workload** | v8-v7 suite (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes) run daily in CI by a third party on ubuntu, macOS arm64 and windows runners. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu, macos-arm64 and windows runners; CPU models not stated. |
| **Adoption** | 390 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/just-js/lo) · [benchmark](https://github.com/ahaoboy/js-engine-benchmark) |

## Verdict

Third-party daily CI table (ahaoboy/js-engine-benchmark, fork of Mozilla arewefastyet v8-v7, snapshot 2026-10-05): lo 0.0.33.pre (V8 15.2) scored 43804 vs Node 26.10.0 (V8 14.6) 40333 on ubuntu-latest, 52785 vs 37405 on macos-latest arm64 and 40191 vs 35121 on windows-latest, one run each on GitHub-hosted runners with unstated CPUs and stripped prebuilt binaries; d8 15.7 beat lo on all three, and Bun canary and Deno canary scored below lo.

## Use it when

- Self-contained scripts or services you control end to end and can write against lo's own bindings, where you want a single small binary (57 MB vs Node's 111 MB on the ubuntu runner in the benchmark table).
- CPU-bound JavaScript on macOS arm64, where the measured gap to Node 26 is largest (52785 vs 37405 score, about 1.26x even with the Splay test excluded, derived from page data).
- Experiments with V8 Fast API bindings to C libraries, or with tracking new V8 releases quickly (releases moved V8 from 14.4 to 15.2 within August 2026).
- Startup- or footprint-sensitive tooling where Node's bootstrap cost is the problem and Node API compatibility is not needed.

## Skip it when

- Any code that depends on Node.js APIs or npm packages: there is no compatibility layer yet.
- When you only need raw V8 speed: plain d8 15.7 outscored lo on every platform in the same table (ubuntu 48107, macOS arm64 64220, windows 46932), and on windows lo trails Node on Richards and DeltaBlue.
- Production or long-term-support needs: versions are 0.0.x pre-releases, Intl is reported broken (issue #31), and macOS arm64 and Linux arm64 build problems are open (#49, #27).
- Windows deployments that need parity with Linux: the windows margin over Node is about 1.01x once Splay is excluded (derived from page data), and build quirks are open (#55).

## How it is fast

For pure-JavaScript compute it is V8's own JIT, so the edge over Node comes from embedding a newer V8 (lo 0.0.33-pre ships V8 15.2; Node 26.10.0 bundles V8 14.6.202.34) with its own isolate setup and flags ('--use-strict --turbo-fast-api-calls --cppgc-young-generation', 2 platform threads) and no Node bootstrap layer. Native bindings are registered as V8 Fast API calls (v8::CFunction), which TurboFan can call directly instead of through the slow FunctionCallbackInfo path; this matters for I/O-heavy code, not for the v8-v7 suite.

## Compared with alternatives

Pick lo over LLRT when the work is compute-bound: in the same table LLRT scores 972 on ubuntu against lo's 43804, while LLRT's case is Lambda cold start; the other catalogued siblings speed up Python, Ruby, Lua or PHP, not JavaScript.

## Integration

| | |
|---|---|
| **Form** | standalone runtime executable (built with make, or prebuilt release binaries) |
| **Dependencies** | prebuilt libv8_monolith from just-js/v8 releases, libcurl, OpenSSL (libssl), zlib; Visual Studio build tools and make on Windows |
| **Minimum toolchain** | clang/clang++ with C++20 (Makefile default CC=clang, -std=c++20); MSVC cl /std:c++20 on Windows |
| **Platforms** | Linux x64 and arm64, macOS arm64 and x64, Windows x64 |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Default V8 flags in main.h include --use-strict, so every script runs in strict mode; sloppy-mode code (implicit globals, with statements) fails rather than running as it would under Node.
- The Makefile adds -march=native -mtune=native on Linux and macOS arm64, so a binary built on one machine may not run on an older CPU; copy the release binary or build on the target class of host.
- Benchmark harness note (ahaoboy/js-engine-benchmark scripts/update.ts): each engine runs dist/run.js once, sequentially, on a shared GitHub runner, and the engines do not run it in the same mode (Node treats it as an ES module because the repo's package.json sets type: module, lo forces --use-strict, d8 runs it as a classic script); the effect on scores was not measured.
- Most of the macOS and windows lead comes from Node's Splay score collapsing on those runners (15574 and 13056 vs 35204 on ubuntu, while lo and d8 stay near 35000-50000); excluding Splay, lo/Node is about 1.09x ubuntu, 1.26x macOS arm64 and 1.01x windows (derived from page data). The cause of Node's Splay drop is not documented.

## Known shortcomings

- The win over Node 26.10.0 on ahaoboy/js-engine-benchmark comes from V8 embedding and configuration, not a new engine: d8 beats lo on every platform, the biggest gap is GC-heavy Splay, and on Windows lo trails Node on Richards and DeltaBlue. Daily single CI run with the runner CPU unstated.
- Enricher: the lead is mostly V8 version (lo 0.0.33-pre ships V8 15.2 against Node 26.10.0's V8 14.6.202.34) and Node's Splay collapse on macOS and Windows (15574 and 13056 vs 35204 on ubuntu); excluding Splay, lo over Node is 1.09x on ubuntu, 1.26x on macOS arm64 and 1.01x on Windows (derived). The harness runs each engine once, sequentially and in different modes (Node treats run.js as ESM via package.json type module, lo forces --use-strict); the Makefile uses -march=native.

## Caveats and trade-offs

lo's own README makes no performance claim; the evidence is only the third-party daily table (snapshot of 2026-10-05, lo 0.0.33.pre, Node 26.10.0 via setup-node 'latest'; prebuilt stripped binaries installed by ahaoboy/js-engine-setup), which is regenerated every day so the numbers drift. Because lo embeds V8, the gap to Node reflects V8 version, flags and heap/runtime setup rather than a new engine: the largest per-test gaps are on GC-heavy Splay (macOS 49432 vs 15574, windows 35017 vs 13056), on windows lo trails Node on Richards (32563 vs 34370) and DeltaBlue (71216 vs 74561), and plain V8 d8 scores higher than lo on every platform (ubuntu 48107, macOS arm64 64220, windows 46932). The v8-v7 suite is old, each platform is one CI run per day, and hardware is whatever the GitHub runner provides. [retier] lo 0.0.33-pre ships V8 15.2 while Node 26.10.0 bundles V8 14.6.202.34, so the lead is mostly engine version and configuration, not a new engine; d8 beats lo on every platform and on Windows lo trails Node on Richards and DeltaBlue. The harness runs each engine once, sequentially and in different modes (Node runs run.js as ESM, lo forces --use-strict), daily on an unnamed CI runner; lo builds with -march=native.

V8-based runtime with custom C++ bindings and assembly builtins, x64 and arm64; minimal Node.js API compatibility; builds link system libssl and zlib plus a custom libcurl.

## Maintenance

Active (ten pre-releases from 0.0.24-pre to 0.0.33-pre in August 2026, last commit 2026-09-16) and MIT-licensed, but still pre-1.0 with its own non-Node API, so treat it as an experimental runtime rather than a Node replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (ahaoboy/js-engine-benchmark, a fork of Mozilla arewefastyet's v8-v7 benchmarks, run daily by .github/workflows/update.yml) shows lo's total score above Node 26.10.0 on all three platforms; the benchmark code is public but compiler/flags of the prebuilt binaries and runner CPU models are not stated, so not A.
- **Verifier notes:** All six scores in claimed_speedup match the ubuntu, macos-arm64 and windows Score rows of the README table dated 10/5/2026, and lo is above Bun and Deno on all three (windows margin over Deno is small: 40191 vs 39991). Shortcomings: win over Node is a V8 embedding/config effect, not an engine; d8 itself beats lo everywhere; daily single CI runs on unspecified runner CPUs. Metadata checked: MIT, 390 stars, last commit 2026-09-16.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://github.com/just-js/lo>
  - <https://github.com/just-js/lo/commits>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/README.md>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/just-js/lo>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/README.md>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/Makefile>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/main.cc>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/main.h>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/lo.cc>
  - <https://raw.githubusercontent.com/just-js/lo/HEAD/lo.h>
  - <https://github.com/just-js/lo/issues>
  - <https://github.com/just-js/lo/releases>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/package.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/build.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/nodejs/node/v26.10.0/deps/v8/include/v8-version.h>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/just-js/lo`) · [data/wave12/enrich/raw/github_com_just_js_lo.json](../../../data/wave12/enrich/raw/github_com_just_js_lo.json) (enrichment confidence 0.6)

</details>
