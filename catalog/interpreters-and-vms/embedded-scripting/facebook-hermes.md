# Hermes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Meta's AOT-bytecode JavaScript engine for React Native; roughly halves app start-up versus JavaScriptCore by skipping parsing at launch.

| | |
|---|---|
| **Beats** | JavaScriptCore as shipped in stock React Native (start-up, memory, binary size); QuickJS for the throughput charts in the repo's own blog. V8, the listed baseline, is not compared on any page opened (Kudo/react-native-js-benchmark compares JSC, V8 and Hermes, but its results are in Google Sheets that are blocked here). |
| **Claimed result** | Mattermost app start-up (time from pressing the app icon to the first screen rendered), Hermes vs stock React Native on JavaScriptCore: Android (Samsung Galaxy S20) 1.97 s vs 0.96 s, '51% faster' (about 2.05x, derived from page data); iOS (iPhone 12 Pro) 0.52 s vs 0.19 s, '63% faster' (about 2.7x, derived from page data). Same page: raw APK (arm64-v8a) 72.1 MB vs 58.2 MB, IPA 23.2 MB vs 27.6 MB (+4.4 MB, larger with Hermes), memory 398 MB vs 305 MB (Android) and 120 MB vs 107 MB (iOS). Throughput (repo doc/blog/2025-07-15, bar charts relative to QuickJS = 1.0, values read off the chart): stable Hermes interpreter about 0.96x-2.0x QuickJS across Octane plus three React benchmarks (zlib slightly slower); static_h 'Hermes v2' interpreter about 1.6x-4.6x and with JIT about 2.0x-5.6x. |
| **Workload** | Mattermost React Native app: cold start-up (app icon press to first screen rendered), memory over a couple of minutes of identical use, and APK/IPA size, on Android and iOS; separately Octane benchmarks plus custom React benchmarks (benchmarks/ in the repo) relative to QuickJS. |
| **Metric** | throughput |
| **Hardware** | Samsung Galaxy S20 (Android) and iPhone 12 Pro (iOS) for the start-up numbers; Raspberry Pi 3 and Raspberry Pi 5 for the 2024 Octane charts; the 2025 QuickJS-relative charts state no hardware. |
| **Compiler and flags** | Hermes: cmake -G Ninja -DCMAKE_BUILD_TYPE=Release for the main and static_h branches; QuickJS: plain make; compiler not named (macOS only harness) |
| **Adoption** | 11.3k stars, 874 forks; default JavaScript engine of React Native since 0.70 |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/facebook/hermes) · [benchmark](https://reactnative.dev/blog/2022/07/08/hermes-as-the-default) |

## Verdict

Meta measured the Mattermost React Native app with Hermes versus stock React Native on JavaScriptCore: start-up (icon press to first rendered screen) 0.96 s versus 1.97 s on a Samsung Galaxy S20 and 0.19 s versus 0.52 s on an iPhone 12 Pro, with memory 305 MB versus 398 MB and 107 MB versus 120 MB, the APK 13.9 MB smaller and the IPA 4.4 MB larger; engine versions, build flags and repetition counts are not published. Separate first-party bar charts (no hardware or QuickJS version stated) put the Hermes V1 interpreter at about 1.6x-4.6x and Hermes V1 with JIT at about 2.0x-5.6x QuickJS on Octane plus three React benchmarks.

## Use it when

- React Native apps where cold-start time to first screen matters: Meta's Mattermost measurement shows 1.97 s to 0.96 s on a Galaxy S20 and 0.52 s to 0.19 s on an iPhone 12 Pro against stock RN on JavaScriptCore.
- Memory-constrained mobile or embedded hosts running a large, known JS bundle that can be compiled to bytecode at build time (Android APK 13.9 MB smaller and 93 MB less memory in the same test).
- UI threads that cannot tolerate long GC pauses: Hades reports 48 ms p99.9 pauses on 64-bit devices versus GenGC's 1.4 s p99 on Facebook for Android.
- C++ hosts that want a JS engine much faster than QuickJS on Octane-style code (Hermes V1 interpreter about 1.6x-4.6x QuickJS per Meta's June 2025 chart) without bundling V8.

## Skip it when

- Peak-throughput server or desktop JS: no page read compares Hermes with V8 or with JavaScriptCore's full JIT on throughput, and Meta deliberately chose not to build a JIT for the legacy Hermes line (the static_h JIT is optional).
- Code that depends on local eval, with, Symbol.species, spec-exact non-strict arguments behaviour, Function.prototype.toString source text or a built-in ES module loader: Hermes documents these as excluded or deviating.
- Running untrusted JavaScript in-process: Hermes has had critical type-confusion CVEs exploitable by crafted JS (CVE-2020-1911, CVSS 9.8, fixed in hermes-engine 0.5.2), and Meta notes such bugs matter only if the app evaluates untrusted JS.
- Apps that load JS source at run time rather than shipping bytecode: the start-up win comes from precompiled bytecode, so it does not carry over to source loaded at run time.
- Small-footprint hosts that need a minimal, self-contained engine: the build needs CMake, Ninja, Python and ICU, and the iOS IPA grew 4.4 MB with Hermes in Meta's own test.

## How it is fast

Start-up: parsing and compilation move to build time, so launch only loads precompiled, optimized register-based bytecode (variable-length instructions, 1-byte register operands, constants loaded through dedicated opcodes and a string table) instead of parsing source. Memory: Hades, a mostly concurrent snapshot-at-the-beginning mark-sweep old generation, plus pointer compression and small-integer encoding (HV32: 32-bit values with heap-boxed doubles that do not fit). Throughput in Hermes V1 (static_h) comes from a new compiler with type inference over untyped JS, an optional baseline JIT for hot functions, and optional AOT native compilation of typed JS.

## Compared with alternatives

Pick Hermes over QuickJS, PrimJS or Escargot when you ship a React Native or other mobile app whose JS bundle can be compiled to bytecode at build time and start-up, memory and GC pauses matter most; pick QuickJS (or PrimJS) when you need a tiny, spec-complete engine with eval and ES modules from source text, and V8 when peak JIT throughput matters more than footprint.

## Integration

| | |
|---|---|
| **Form** | shared lib (libhermes via JSI C++ API) plus CLI tools (hermes, hermesc, hvm, hbcdump); in React Native it is built and shipped by RN itself |
| **Dependencies** | CMake, Ninja, Python and ICU to build (libicu-dev on Linux); libreadline optional for the REPL |
| **Minimum toolchain** | C++17; clang, gcc or Visual C++ (Visual Studio 2019 generator in the Windows instructions; CI now uses VS 2026) |
| **Platforms** | Android and iOS (primary), macOS, Linux, Windows; HV32 by default on Android and HV64 on iOS in Hermes V1; JIT availability per platform not documented in the sources read |
| **Thread safety** | not documented in the sources read; Hades does its old-generation marking on a background thread on 64-bit devices (incremental, single-threaded on 32-bit) |
| **Drop-in for the baseline** | partial: a supported engine swap inside React Native (the default since RN 0.70; RN 0.84 documents an opt-out back to legacy Hermes); outside React Native it exposes JSI, hermes_abi and N-API rather than V8's or JSC's embedding APIs, and its spec deviations can break code that runs on V8 |

## Gotchas

- The headline numbers are first-party (Meta's React Native blog, 2022) on one app, Mattermost, timed from icon press to first screen with no published harness, run count, variance, engine versions or build flags; '51% faster' and '63% faster' are time reductions, about 2.05x and 2.7x as speed ratios (derived from page data). The baseline is JavaScriptCore in stock React Native, not V8.
- The QuickJS-relative throughput charts (doc/blog 2025-07-15, Hermes V2 measured as hv32 with and without JIT) give no QuickJS version, compiler flags or hardware, and the repo's benchmarks/bench-runner only has Hermes, V8 and V8 --jitless runners (Hermes runs bytecode precompiled with -O), so the QuickJS columns cannot be reproduced from the repo; legacy Hermes is about level with QuickJS on zlib.
- Bytecode is version-locked: Hermes bumped the bytecode version 98 to 99 for release 260318099.0.0 and prebuilt bytecode must be rebuilt; the README warns each Hermes release targets a specific React Native version and a mismatch can crash the app.
- Hades trades throughput for pause time (more expensive write barriers, freelist allocation instead of bump-pointer, more fragmentation), and Promise is a bytecode polyfill whose microtask timing differs from the spec in some async and subclass cases.

## Known shortcomings

- Meta's own start-up numbers on one app (Mattermost against stock React Native on JavaScriptCore: Galaxy S20 1.97 s vs 0.96 s, iPhone 12 Pro 0.52 s vs 0.19 s), harness and flags unpublished; the baseline is JavaScriptCore rather than the listed V8, the iOS IPA grows by 4.4 MB, stable Hermes is about level with QuickJS on zlib in the repo's own charts, and the Callstack independent 40% start-up figure was seen only as a quote and search snippet.
- Enricher: the QuickJS charts in the repo are not reproducible (benchmarks/bench-runner has only Hermes, V8 and V8 --jitless runners; QuickJS version, flags and hardware unstated); CVE-2020-1911 (CVSS 9.8) for untrusted JavaScript, bytecode version lock (98 to 99), spec deviations (local eval, with). Hermes V1 is the default since React Native 0.84 (2026-02-11).

## Caveats and trade-offs

Start-up, memory and size numbers are first-party (Meta's React Native blog, 2022) on one app (Mattermost) with no published harness, build flags or engine versions; the 'faster' percentages are time reductions (51% and 63%), not speedup factors. The win comes mostly from shipping precompiled bytecode instead of parsing source at start-up; Hermes has no JIT in stable releases, and the JavaScriptCore it replaced in React Native runs with limited JIT (Kudo/react-native-js-benchmark notes React Native Android does not enable all JSC JIT tiers), so this is not a throughput claim against a full JIT engine. IPA size grows by 4.4 MB on iOS. Callstack's independent iOS measurement (about 40% faster start-up and about 18% less memory than JSC for Mattermost, 2.4 MiB size overhead) is seen only as quoted in reactnative.dev's 2021 post 'Toward Hermes being the Default' and in a search snippet; callstack.com is blocked here. Throughput charts against QuickJS are first-party bar charts without exact values or compiler flags; stable Hermes is about level with QuickJS on zlib. Other in-repo figures (JSON.parse 2.7x-3.4x faster, Hades GC 34x shorter p99.9 pauses, static_h 1.1x-7.9x on Octane) compare Hermes with older Hermes, not with a baseline.

Executable 27M vs 620K for QuickJS in Bellard's table; built for React Native with precompiled bytecode and startup in mind; Hermes releases are tied to a specific React Native version per the README.

## Maintenance

Actively developed by Meta (default branch static_h, last commit 2026-10-05, Hermes V1 the React Native default since RN 0.84), MIT-licensed and buildable standalone with CMake, but its release cadence, bytecode versions and API are tied to React Native.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now C.
- **Tier reason:** Upgraded from D: Meta's React Native blog post 'Hermes as the Default' (source in facebook/react-native-website) gives first-party start-up, size and memory numbers for the Mattermost app with Hermes versus stock React Native on JavaScriptCore, on a Samsung Galaxy S20 and an iPhone 12 Pro; no measurement harness, build flags or engine versions are published, so not A, and the publisher is the project owner, so not B. The in-repo blog (doc/blog) adds first-party Octane-style charts against QuickJS whose benchmark code is public (benchmarks/octane, benchmarks/bench-runner) but with no compiler flags and, for the 2025 charts, no hardware.
- **Verifier notes:** The original benchmark_url (repo front page) has no numbers and no baseline comparison (the two false flags refer to it); the corrected benchmark_url was read from its source file in facebook/react-native-website, including the two result images. Metadata checked on github.com: MIT, 11.3k stars, not archived, default branch static_h, last commit 2026-10-05, so active and copyable. Shortcomings to record: first-party single-app start-up numbers without harness or flags, baseline is JavaScriptCore not the listed V8, iOS binary grows 4.4 MB, QuickJS throughput charts are approximate and stable Hermes is not faster on zlib.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/facebook/hermes>
  - <https://github.com/facebook/hermes/commits/static_h>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/README.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2025-07-15-static-h-performance-june-2025.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2024-11-09-octane-benchmark-jit-progress.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2024-12-19-static-hermes-update-dec-2024.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2025-11-24-json-parsing-performance.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2026-06-05-new-hermes-stable-release.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/images/2025-07-15-perf-hv32-jit.jpeg>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/images/2025-07-15-perf-hv32-interpreter.jpeg>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/images/2024-11-09-octane-pi5.jpeg>
  - <https://github.com/facebook/hermes/tree/static_h/benchmarks>
  - <https://github.com/facebook/react-native-website/tree/main/website/blog>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/blog/2019-07-17-hermes.md>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/blog/2021-10-26-toward-hermes-being-the-default.mdx>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/blog/2022-07-08-hermes-as-the-default.mdx>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/static/blog/assets/hermes-default-android-data.png>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/static/blog/assets/hermes-default-ios-data.png>
  - <https://github.com/Kudo/react-native-js-benchmark>
  - <https://raw.githubusercontent.com/Kudo/react-native-js-benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/README.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2025-07-15-static-h-performance-june-2025.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2024-11-09-octane-benchmark-jit-progress.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2024-12-19-static-hermes-update-dec-2024.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2026-06-05-new-hermes-stable-release.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2025-11-02-hermes-compilation-runtime-modes.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/2025-11-06-hermes-memory-modes.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/images/2025-07-15-perf-hv32-jit.jpeg>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/images/2025-07-15-perf-hv32-interpreter.jpeg>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/blog/images/2024-11-09-octane-pi5.jpeg>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/BuildingAndRunning.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/Features.md>
  - <https://raw.githubusercontent.com/facebook/hermes/HEAD/doc/Design.md>
  - <https://github.com/facebook/hermes/tree/static_h/benchmarks>
  - <https://github.com/facebook/hermes/tree/static_h/benchmarks/bench-runner>
  - <https://raw.githubusercontent.com/facebook/hermes/static_h/benchmarks/bench-runner/README.md>
  - <https://raw.githubusercontent.com/facebook/hermes/static_h/benchmarks/bench-runner/runner.py>
  - <https://raw.githubusercontent.com/facebook/hermes/static_h/benchmarks/bench-runner/bench-runner.py>
  - <https://raw.githubusercontent.com/facebook/hermes/static_h/benchmarks/bench-runner/categories.py>
  - <https://github.com/facebook/hermes/tree/static_h/benchmarks/jit-benches>
  - <https://github.com/facebook/hermes/tree/static_h/benchmarks/octane>
  - <https://raw.githubusercontent.com/facebook/hermes/static_h/benchmarks/octane/raytrace.js>
  - <https://github.com/facebook/hermes/tree/static_h/API>
  - <https://github.com/facebook/hermes/commits/static_h>
  - <https://github.com/facebook/hermes/releases>
  - <https://github.com/facebook/hermes/security>
  - <https://github.com/advisories/GHSA-f5x2-xv93-4p23>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/blog/2022-07-08-hermes-as-the-default.mdx>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/static/blog/assets/hermes-default-android-data.png>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/static/blog/assets/hermes-default-ios-data.png>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/blog/2021-10-26-toward-hermes-being-the-default.mdx>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/blog/2019-07-17-hermes.md>
  - <https://raw.githubusercontent.com/facebook/react-native-website/main/website/blog/2026-02-11-react-native-0.84.mdx>
  - WebSearch: Hermes V1 default engine React Native 0.84 static_h JIT (snippets only)
  - WebSearch: Hermes CVE type confusion advisories (snippets only; CVE-2023-23557 and CVE-2023-25933 seen only in snippets)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/facebook/hermes`) · [data/wave12/enrich/raw/github_com_facebook_hermes.json](../../../data/wave12/enrich/raw/github_com_facebook_hermes.json) (enrichment confidence 0.75)

</details>
