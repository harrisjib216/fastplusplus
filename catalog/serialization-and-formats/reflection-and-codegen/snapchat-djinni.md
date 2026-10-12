# Djinni (Snapchat fork of dropbox/djinni)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Snap's maintained Djinni IDL bridge generator (C++ to Java/JNI, Objective-C, WASM/TypeScript); claims 5-10x faster JNI string passing than Dropbox's original.

| | |
|---|---|
| **Beats** | original dropbox/djinni generated JNI string conversion (Java to C++ string passing); the README names no baseline explicitly |
| **Claimed result** | 'Speed up string passing between Java and C++ (about 5-10x faster depending on string size)'. |
| **Workload** | Passing strings between Java and C++ through Djinni-generated JNI glue; the README's 'Modifications' list gives one line and no benchmark, string sizes, device or version. |
| **Metric** | latency |
| **Adoption** | 238 stars (Snapchat/djinni); dropbox/djinni has 2.9k stars and is archived |
| **Last commit** | 2024-10-28 |
| **Links** | [repository](https://github.com/Snapchat/djinni) · [benchmark](https://github.com/Snapchat/djinni) |

## Verdict

The only performance evidence is the fork README's one-line, first-party claim that string passing between Java and C++ is about 5-10x faster than Dropbox's handwritten conversion, with no device, string sizes, Android/NDK version or compiler flags. The repo's Android perftest prints absolute timings for the fork only (for example argString 16 chars at 4,622 ns and the row labelled 16384, really 23,760 ASCII chars, at 109,606 ns; returnString 16,384 chars at 230,499 ns), on an unnamed device and build mode; a search snippet of Snap's 2021 'Improving Djinni' post mentions string marshalling gains (a newsletter summary says 3-10x) but the post (eng.snap.com) is blocked here.

## Use it when

- Mobile apps sharing one C++ core across Android (JNI), iOS (ObjC/Swift) and the web (WASM), where hand-written JNI glue is the alternative.
- Projects still on archived dropbox/djinni that pass strings across the JNI boundary often and want the cheaper conversion plus bug fixes.
- Interfaces that move primitive vectors: declare them array&lt;i32/i64/f64&gt; instead of list&lt;&gt; to avoid per-element boxing (perftest example: argArrayInt 128 at 8,210 ns versus argListInt 128 at 353,718 ns, about 43x, derived from page data).
- Large binary payloads that should not be copied per call: use DataView (borrowed direct ByteBuffer/NSData) or DataRef (owned, can steal a std::vector&lt;uint8_t&gt; or std::string buffer).

## Skip it when

- Strings that may carry invalid UTF-8 from C++ or unpaired surrogates from Java (for example a Java String cut in the middle of an emoji): the fork throws std::range_error where Dropbox substituted U+FFFD; the maintainer calls this intentional (issue #86) and points to binary/DataView/DataRef for non-text data.
- Builds that must move to C++26 or treat deprecation warnings as errors: the string path relies on std::wstring_convert/std::codecvt_utf8_utf16 (deprecated in C++17, removed in C++26); issue #199 reports 14 -Wdeprecated-declarations warnings on Android with C++20 on main.
- Teams that cannot install Bazel and a JVM: the code generator is built and run through Bazel (README FAQ), even though generated files can go into any build system.
- Apps with very many live interface objects on Android: each interface object crossing JNI holds one JNI global reference, and the README warns the limit is usually about 64k.
- If you need a measured, reproducible speedup: the 5-10x string claim has no published before/after benchmark, and the bundled perftest only times the fork itself.

## How it is fast

The string speedup comes from replacing Dropbox's per-code-point miniutf transcoding (a validating decode and an initializer-list append for every code point) with bulk std::wstring_convert&lt;std::codecvt_utf8_utf16&lt;char16_t&gt;&gt; conversion from the platform C++ library, followed by one NewString call. Separately, array&lt;T&gt; marshals primitive element types through GetPrimitiveArrayCritical and a single copy into a Java T[], where list&lt;T&gt; boxes each element through a Long.valueOf JNI call; DataView/DataRef expose direct ByteBuffers via GetDirectBufferAddress instead of copying.

## Compared with alternatives

None of the catalogued siblings in this category (Cista++, struct_pack, bitsery, YAS, FBE, the enum-reflection libraries) generates cross-language call bindings; pick Djinni when the bottleneck is calling C++ from Java/Kotlin, ObjC/Swift or JS, and pair it with one of those serializers over DataView/DataRef if you need to move structured data in bulk rather than per-field.

## Integration

| | |
|---|---|
| **Form** | source-drop (generated C++/JNI/ObjC++/WASM sources plus support-lib sources compiled into your app); the generator is a Scala binary built with Bazel |
| **Dependencies** | Bazel and a JVM to build/run the generator; at run time JNI (Android/JVM), the Objective-C runtime (Apple), or Emscripten Embind (WASM); optional Protobuf for protobuf types |
| **Minimum toolchain** | main branch: C++17 (.bazelrc passes -std=c++17; README pins Android SDK 30.0.2 and NDK 21.4.7075529 for the examples). experimental-record branch (the one Snap uses): C++20, Bazel 8.5.0+, Java 8+ |
| **Platforms** | Android and desktop JVM via JNI, iOS/macOS via Objective-C (Swift and C API backends on experimental-record per open PR #225), browsers via WASM/TypeScript |
| **Thread safety** | not documented in the fork README |
| **Drop-in for the baseline** | partial: the IDL is a superset of dropbox/djinni and output must be regenerated; generated code differs (CppProxy finalizers removed, invalid UTF now throws, and on experimental-record records become mutable with optionals omitted from constructors unless --\*-legacy-records is passed) |

## Gotchas

- Code-read finding: jniUTF8FromString and jniWStringFromString (support-lib/jni/djinni_support.cpp on main and experimental-record) call GetStringChars without a null check and release it with a plain ReleaseStringChars after the conversion, not through an RAII guard; when Utf8Converter::to_bytes throws std::range_error on a lone surrogate, ReleaseStringChars is skipped and the chars buffer is leaked or left pinned. Dropbox's original used a unique_ptr deleter. (Inferred from the code, not tested.)
- Perftest harness flaw: MainActivity.kt builds its test strings with Kotlin inclusive ranges (for i in 0..lowCount/minCount), so the rows labelled argString 128/4096/16384 actually pass 144, 4,752 and 23,760 characters; all strings are ASCII ('1234567890ABCDEF' and '@'), the best case for UTF transcoding; there is no warm-up and each row averages 1,000 single-call nanoTime samples including outliers (row maxima up to 5.3 ms; returnString 16384 max 1.92 ms). The rows labelled argArrayRecord/returnArrayRecord are declared list&lt;RecordSixInt&gt; in djinni_perf_benchmark.djinni, so they measure list&lt;&gt;.
- The perftest build documents no optimization level: README says 'bazel build perftest', and neither .bazelrc nor perftest/BUILD or support-lib/BUILD sets -c opt or -O flags, so the example output may come from Bazel's default fastbuild mode (not stated). That would also favor a precompiled libc++ codecvt over inline hand-written code in any before/after comparison.
- Two live lines: main has had no commit since 2024-10-28, while Snap develops on experimental-record (commits to 2026-10-09; open PR #225 merges 224 commits into main), which changes record semantics and raises the toolchain to C++20/Bazel 8.5.

## Known shortcomings

- The '5-10x faster string passing' claim is one README line with no before/after numbers; the perftest app shows fork-only nanosecond timings with no device named and its ArrayRecord rows are really list&lt;&gt;. The fork's string path uses std::wstring_convert (deprecated in C++17, removed in C++26) and throws std::range_error on invalid UTF where Dropbox's code substituted U+FFFD (inferred from code, not tested). Stale (last commit 2024-10-28).
- Enricher: the 5-10x string claim is unverifiable (perftest only times the fork, never the Dropbox original); the perftest harness uses Kotlin inclusive ranges so the 128/4096/16384 rows really pass 144/4,752/23,760 chars, ASCII only, no warm-up, no optimisation flag anywhere (likely Bazel fastbuild). jniUTF8FromString and jniWStringFromString call GetStringChars with no null check and no RAII release, so a std::range_error on a lone surrogate leaks or leaves the chars buffer pinned; throw-on-invalid-UTF is intentional (issue #86); codecvt deprecation warnings (#199). Development continues on the experimental-record branch (commits to 2026-10-09, C++20, Bazel 8.5, PR #225 open), so the project is active, not stale.

## Caveats and trade-offs

First-party one-line claim with no baseline version, string sizes, device or method. The repo has an Android perftest app (perftest/, djinni_perf_benchmark.djinni) whose README shows example output for the fork alone (argString 16/128/4096/16384: 4,622/4,893/24,407/109,606 ns average; returnString same sizes: 5,285/5,605/57,891/230,499 ns) but no run of the original Dropbox code and no device or Android/NDK version, so the 5-10x figure cannot be checked from it. Code reading: the original dropbox/djinni support-lib/jni/djinni_support.cpp converts strings with miniutf-derived handwritten UTF-8/UTF-16 code that substitutes U+FFFD for invalid sequences and unpaired surrogates; the Snapchat fork's jniStringFromUTF8/jniUTF8FromString now use std::wstring_convert with std::codecvt_utf8_utf16, which is deprecated since C++17 and removed in C++26, and which throws std::range_error on invalid input instead of substituting (a behavior change for malformed UTF-8 or lone surrogates; inferred from the standard, not tested). A search snippet of Snap's engineering post (eng.snap.com, blocked here) said a 16 KB string took more than 2 ms through the original handwritten conversion on a fairly fast device; not verified. dropbox/djinni itself makes no performance claim, so only the fork's string-passing change has evidence. The 'array&lt;&gt; is an order of magnitude faster than list&lt;&gt;' line compares two Djinni types; the perftest example output supports it (argListInt 128: 353,718 ns vs argArrayInt 128: 8,210 ns, about 43x, derived from page data), but argArrayRecord is declared as list&lt;RecordSixInt&gt; in djinni_perf_benchmark.djinni, so the 'ArrayRecord' rows actually measure list&lt;&gt;.

Cross-language binding generator (C++ with Java/JNI, Objective-C and WASM/TypeScript), not a scripting engine. The fork switched the build from sbt/gyp to Bazel, added array&lt;&gt;, outcome&lt;&gt;, future&lt;&gt; and protocol generation, and removed CppProxy finalizers. The djinni.xlcpp.dev documentation site named in the lead belongs to the separate cross-language-cpp djinni-generator and support-lib, whose README has no performance claim.

## Maintenance

Apache-2.0 and copyable; the record's 'stale' status reflects only the main branch (last commit 2024-10-28): Snap actively maintains the experimental-record branch (commits through 2026-10-09, merge PR #225 open since 2026-10-08), so treat the project as active but expect a C++20/Bazel 8.5 jump and record-semantics changes when that branch lands.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Modifications' list carries a one-line first-party claim, 'Speed up string passing between Java and C++ (about 5-10x faster depending on string size)', against the original Dropbox string conversion, with no benchmark, string sizes, device or version. The repo's perftest app (perftest/README.md) reports absolute nanosecond timings for the fork only, with no before/after comparison and no device named, so the claim stays tier C.
- **Verifier notes:** Claim text is quoted accurately; record otherwise correct. Shortcomings to record: one-line first-party claim with no methodology or before/after numbers; string path now relies on deprecated std::wstring_convert (removed in C++26) that throws on invalid UTF instead of substituting U+FFFD as the Dropbox original did; perftest mislabels list&lt;&gt; rows as array. Metadata confirmed: 238 stars, 64 forks, Apache-2.0, not archived, not a GitHub fork (README says it continues dropbox/djinni), last commit 2024-10-28 (stale). The category reflection-and-codegen is not one of wave 12's four categories; the orchestrator may want to check the filing.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-100 (wave 12); enricher w12 pair-008
- **Pages the verifier opened:**
  - <https://github.com/Snapchat/djinni>
  - <https://raw.githubusercontent.com/Snapchat/djinni/HEAD/README.md>
  - <https://raw.githubusercontent.com/Snapchat/djinni/HEAD/LICENSE>
  - <https://github.com/Snapchat/djinni/commits>
  - <https://github.com/Snapchat/djinni/tree/main/perftest>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/perftest/README.md>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/perftest/djinni_perf_benchmark.djinni>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/support-lib/jni/djinni_support.cpp>
  - <https://raw.githubusercontent.com/dropbox/djinni/master/support-lib/jni/djinni_support.cpp>
- **Sources the enricher read:**
  - <https://github.com/Snapchat/djinni>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/README.md>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/LICENSE>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/WORKSPACE>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/.bazelrc>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/support-lib/BUILD>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/support-lib/jni/djinni_support.cpp>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/support-lib/jni/djinni_support.hpp>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/support-lib/jni/Marshal.hpp>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/support-lib/jni/DataView_jni.hpp>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/support-lib/jni/DataRef_jni.cpp>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/perftest/README.md>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/perftest/djinni_perf_benchmark.djinni>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/perftest/BUILD>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/perftest/handwritten-src/cpp/DjinniPerfBenchmarkImpl.cpp>
  - <https://raw.githubusercontent.com/Snapchat/djinni/main/perftest/android/app/src/main/java/com/snapchat/djinni/benchmark/MainActivity.kt>
  - <https://github.com/Snapchat/djinni/tree/main/perftest/android>
  - <https://github.com/Snapchat/djinni/tree/main/perftest/android/app/src/main>
  - <https://github.com/Snapchat/djinni/tree/main/perftest/android/app/src/main/java/com/snapchat/djinni/benchmark>
  - <https://github.com/Snapchat/djinni/tree/main/perftest/handwritten-src/cpp>
  - <https://github.com/Snapchat/djinni/tree/experimental-record/perftest>
  - <https://raw.githubusercontent.com/Snapchat/djinni/experimental-record/README.md>
  - <https://raw.githubusercontent.com/Snapchat/djinni/experimental-record/support-lib/jni/djinni_support.cpp>
  - <https://github.com/Snapchat/djinni/commits/main>
  - <https://github.com/Snapchat/djinni/commits/experimental-record>
  - <https://github.com/Snapchat/djinni/pull/225>
  - <https://github.com/Snapchat/djinni/issues?q=is%3Aissue+string>
  - <https://github.com/Snapchat/djinni/issues/86>
  - <https://github.com/Snapchat/djinni/issues/199>
  - <https://raw.githubusercontent.com/dropbox/djinni/master/support-lib/jni/djinni_support.cpp>
  - https://eng.snap.com/improving_djinni (blocked: ENOTFOUND; WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/snapchat/djinni`) · [data/wave12/enrich/raw/github_com_snapchat_djinni.json](../../../data/wave12/enrich/raw/github_com_snapchat_djinni.json) (enrichment confidence 0.5)

</details>
