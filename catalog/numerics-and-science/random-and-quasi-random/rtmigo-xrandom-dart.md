# xrandom (rtmigo/xrandom_dart, Dart random number generators)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Dart` · `MIT` · 🔴 abandoned

> Pure-Dart PRNG classes (xorshift, xoshiro, splitmix64, mulberry32) implementing dart:math Random; Xrandom is 1.4-1.7x faster than Random on AOT.

| | |
|---|---|
| **Beats** | Dart core dart:math Random |
| **Claimed result** | README (ms, lower is better): Xrandom (Xorshift32) 627 / 640 / 391 versus dart:math Random 895 / 929 / 662 for nextInt / nextDouble / nextBool; about 1.43x, 1.45x and 1.69x faster (derived from page data). Xorshift128, Xorshift64, Mulberry32, Xorshift128p and Splitmix64 also beat Random on all three calls; Qrandom/Drandom (Xoshiro128pp) 933 / 1219 / 398 and Xoshiro256pp 1138 / 1182 / 406 are slower than Random for nextInt and nextDouble but faster for nextBool. |
| **Workload** | Time in milliseconds for nextInt, nextDouble and nextBool calls (iteration count not stated), AOT-compiled binaries. |
| **Metric** | throughput |
| **Hardware** | AMD A9-9420e, Ubuntu 20.04 |
| **Compiler and flags** | Dart AOT-compiled binaries, flags and SDK version not stated |
| **Adoption** | 11 stars |
| **Last commit** | 2022-03-15 |
| **Links** | [repository](https://github.com/rtmigo/xrandom_dart) · [benchmark](https://github.com/rtmigo/xrandom_dart) |

## Verdict

First-party README tables (AOT-compiled binaries on an AMD A9-9420e under Ubuntu 20.04, milliseconds, iteration count, Dart SDK version and benchmark harness not published) show Xrandom at 627 / 640 / 391 ms versus dart:math Random at 895 / 929 / 662 ms for nextInt / nextDouble / nextBool, about 1.43x, 1.45x and 1.69x (derived from page data); Xorshift64 has the fastest nextDouble at 569 ms. The nextInt figures predate the 0.7.1 uniformity fix.

## Use it when

- Dart or Flutter code that calls Random.nextInt, nextDouble or nextBool in hot loops (games, procedural generation, sampling) on native AOT targets.
- Code that needs the same random sequence on Dart VM, AOT and JavaScript builds, or across future SDK versions, from a fixed seed (use Xrandom, Qrandom or Xorshift128 when JavaScript is a target).
- Tests needing reproducible random input: Drandom or Qrandom.seeded() give fixed, reference-checked sequences.
- Cross-language reproducibility, where a Dart port must match numbers produced by the C reference xoshiro128++, xorshift or splitmix64 code with the same seed.

## Skip it when

- Cryptographic use: the classes are xorshift, xoshiro, splitmix64 and mulberry32 generators with clock-based default seeds, not cryptographic generators.
- When quality matters more than speed: the README itself points computational work at Qrandom (xoshiro128++), and Qrandom/Drandom (933 / 1219 ms) and Xoshiro256pp (1138 / 1182 ms) are slower than dart:math Random (895 / 929 ms) for nextInt and nextDouble; only nextBool is faster for them.
- Web targets with the 64-bit generators: Xorshift64, Xorshift128p, Splitmix64, Mulberry32 and the Xoshiro256 classes throw Unsupported64Error under JavaScript.
- Projects that need an actively maintained dependency: last release 0.7.2 on 2022-03-15 and no commits since.
- Measured speed on JavaScript or Flutter mobile targets: the README only benchmarks AOT binaries on one x86 laptop CPU.

## How it is fast

The default Xrandom is Marsaglia's xorshift32 (shifts 13, 17, 5), a few shifts and XORs per 32-bit output. nextBool draws one 32-bit word and hands out its bits one at a time, which is why the nextBool gain (391 vs 662 ms) is larger than the nextInt gain. nextInt masks for power-of-two bounds and otherwise uses modulo with a rejection loop; nextFloat converts a single 32-bit word with Doornik's method instead of the two words nextDouble uses.

## Compared with alternatives

It is the only Dart entry in this category; pure-rand (JavaScript/TypeScript) and lemire/fastrand (Python) play the same role in their runtimes, and C++ projects should take the reference xoshiro or SIMD siblings such as simdrng instead. Pick xrandom when Dart or Flutter code needs a faster Random-compatible generator or bit-identical sequences across VM and web builds.

## Integration

| | |
|---|---|
| **Form** | module (Dart pub package xrandom) |
| **Dependencies** | meta ^1.3.0 |
| **Minimum toolchain** | Dart SDK 2.12 (null safety); pubspec constraint is &gt;=2.12.0 &lt;3.0.0, and pub.dev tags the package dart3-compatible |
| **Platforms** | Dart VM and AOT (pub.dev lists Android, iOS, Windows, Linux, macOS) and web; only Xrandom, Qrandom, Drandom and Xorshift128 work when compiled to JavaScript |
| **Thread safety** | not documented; each instance holds mutable state, so give each isolate its own generator |
| **Drop-in for the baseline** | yes |

## Gotchas

- The README timing tables were last edited before release 0.7.1 (2022-03-14), which fixed issue #3: the old nextInt's 'debiased modulo once' check could never trigger with Dart's 64-bit ints, so the nextInt timings were taken on plain, biased modulo code. The current nextInt adds a power-of-two branch and a working rejection loop and has not been re-benchmarked.
- Drandom still overrides nextInt with the old loop (u - (r = u % max) + m &lt; 0), which by the same reasoning never repeats, so Drandom.nextInt is plain modulo and is noticeably biased for large bounds that are not powers of two (finding from reading lib/src/80_drandom.dart; 0.7.1 only narrowed its max to 2^31).
- Unseeded constructors seed from DateTime.now().millisecondsSinceEpoch mixed with the object's hashCode; Xorshift32's clock path does not exclude a zero state, which would make it return 0 forever (explicit seeds are range-checked to 1..0xFFFFFFFF).
- nextInt accepts bounds only up to 2^32 (RangeError above), and sequences differ from dart:math Random for the same integer seed.

## Known shortcomings

- Tier C: README tables (AMD A9-9420e, Ubuntu 20.04) with no benchmark code in lib, test or example. Last commit 2022-03-15, abandoned.
- The README timings predate the 0.7.1 nextInt uniformity fix (issue #3; commit 4367cf3 left the README unchanged), so the nextInt rows measured biased plain-modulo code; Drandom.nextInt still uses a loop that never fires, so it stays plain modulo and biased for large non-power-of-two max (code reading). The benchmark harness is not public (benchmark/ 404). Qrandom and Xoshiro256pp are slower than dart:math Random for nextInt/nextDouble. pub.dev 150/160 points, about 1,649 downloads per 30 days.

## Caveats and trade-offs

Dart only, not callable from C++. Benchmark code is not visible in the repo's top-level listing (lib, test, example, .github), so it is first-party numbers with partial methodology (hardware yes, SDK and iteration count no). The last visible commit is a bot merge from 2022-03-15. Only some of the shipped generators beat the baseline.

Priority is bit-identical output across platforms (VM and JS), checked against C++ reference outputs; offers Xorshift, Xoshiro, Splitmix64 and Mulberry32 variants with the same API as dart:math Random; some generators are slower than the standard Random.

## Maintenance

Abandoned since the 0.7.2 release of 2022-03-15, but MIT, pure Dart with one small dependency, all four GitHub issues closed, 150 of 160 pub points and about 1,650 downloads in the last 30 days, so it is still usable and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Speed and More benchmarks tables compare Xrandom and other generators against dart:math Random (ms, AOT binaries, AMD A9-9420e, Ubuntu 20.04), but no benchmark code is in lib/, test/, test/experimental/ or example/ and the Dart SDK version and iteration count are not stated, so first-party with partial methodology.
- **Verifier notes:** Numbers and hardware line confirmed in README. Metadata checked on github.com: MIT, 11 stars, 1 fork, not archived or a fork, last commit 2022-03-15 by github-actions[bot] (abandoned). README title links to github.com/rtmigo/xrandom, but the record's repo is the actual package repo.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/rtmigo/xrandom_dart>
  - <https://github.com/rtmigo/xrandom_dart/commits>
  - <https://github.com/rtmigo/xrandom_dart/tree/master/test>
  - <https://github.com/rtmigo/xrandom_dart/tree/master/test/experimental>
  - <https://github.com/rtmigo/xrandom_dart/tree/master/example>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/rtmigo/xrandom_dart>
  - <https://github.com/rtmigo/xrandom_dart/issues?q=is%3Aissue>
  - <https://github.com/rtmigo/xrandom_dart/issues/3>
  - <https://github.com/rtmigo/xrandom_dart/tree/master/benchmark>
  - <https://github.com/rtmigo/xrandom_dart/commits/master/README.md>
  - <https://github.com/rtmigo/xrandom_dart/commit/4367cf3>
  - <https://github.com/rtmigo/xrandom_dart/commit/4367cf3.diff>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/README.md>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/pubspec.yaml>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/xrandom.dart>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/src/21_base32.dart>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/src/21_base64.dart>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/src/60_xorshift32.dart>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/src/60_xoshiro128pp.dart>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/src/80_drandom.dart>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/src/90_aliases.dart>
  - <https://raw.githubusercontent.com/rtmigo/xrandom_dart/HEAD/lib/src/00_errors.dart>
  - <https://pub.dev/api/packages/xrandom>
  - <https://pub.dev/api/packages/xrandom/score>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rtmigo/xrandom_dart`) · [data/wave8/enrich/raw/github_com_rtmigo_xrandom_dart.json](../../../data/wave8/enrich/raw/github_com_rtmigo_xrandom_dart.json) (enrichment confidence 0.8)

</details>
