# libqoi

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small C++14 port of the QOI reference codec; a single informal user report says faster than qoixx, which the code does not support.

| | |
|---|---|
| **Beats** | qoixx (wx257osn2/qoixx) |
| **Claimed result** | Issue #1 (2022-07-24, by awesomebytes, author of the ROS PRs): 'About 20% faster to encode and about 30% faster to decode' than qoixx, 640x480 30 fps webcam stream, i7-10875H; no methodology, and implausible from the code (scalar qoi.h port with extra copies, while qoixx reports 1.4-1.7x over qoi.h). ROS image_transport_plugins PRs #103 and #104 report QOI compression at 28% CPU and decompression at 13% CPU keeping 640x480 at 30 fps against PNG transport above 100% CPU at 3 fps; these are CPU-load observations of a transport plugin, not a benchmark. The repo's own tests/benchmark.cpp is disabled and broken (its decode case feeds a PNG to qoi::decode). |
| **Workload** | Encoding and decoding a 640x480, 30 fps webcam stream inside ROS (robotics framework), reported by a third-party user. |
| **Metric** | throughput |
| **Hardware** | Intel i7-10875H @ 2.30GHz x 16, as written in the issue. |
| **Adoption** | 9 stars, 4 forks, 5 commits; used by ROS image_transport_plugins PR #103 (ROS 1, closed unmerged 2025-05-24 for Noetic end of life) and PR #104 (ROS 2, still open, unmerged) |
| **Last commit** | 2022-09-07 |
| **Links** | [repository](https://github.com/ShadowMitia/libqoi) · [benchmark](https://github.com/ShadowMitia/libqoi/issues/1) |

## Verdict

The only number is a third-party issue comment (2022-07-24): 'about 20% faster to encode and about 30% faster to decode' than qoixx on a 640x480 30 fps webcam stream inside ROS on an i7-10875H, with no harness, qoixx version, build type or flags. The same user's ROS PRs report QOI at 28%/13% CPU against PNG over 100% CPU (30 vs 3 fps), which is a property of the format. Read against the code, the qoixx claim is implausible: libqoi is a scalar qoi.h port with extra allocation and zero-fill work, while qoixx publishes 1.4-1.7x over qoi.h, so the gap more likely comes from how each library was wired into the ROS node than from the codec.

## Use it when

- Practically never over the alternatives: the reference qoi.h is equally simple, works from C++ and is maintained; qoixx is measurably faster.
- Only if you need a std::vector-based QOI API under C++14 (qoixx requires C++20) and will vendor and harden the two source files yourself.
- Trusted, in-process image data of normal size (well under about 859 million pixels), where malformed input cannot occur.

## Skip it when

- Decoding untrusted input (network streams, as in the ROS transport it was proposed for): decode() does not check run length against the output size, so a crafted run chunk writes up to 61 pixels past the heap buffer, and headers with 1 or 2 channels overrun it by up to 2 bytes.
- Anything speed-critical: no benchmark in the repository backs a speed claim, and qoixx's README shows qoixx 1.4-1.7x faster than qoi.h on the QOI benchmark suite, while this library is a slower-than-reference port of qoi.h.
- Huge images: width\*height is computed in 32-bit unsigned arithmetic with no pixel limit (qoi.h caps at 400 million pixels), so sizes wrap and the encode output buffer is undersized for RGBA images above about 859 million pixels.
- Projects that need a maintained dependency: README says work in progress with API breaks expected; 5 commits, last 2022-09-07.

## How it is fast

There is no speed technique beyond QOI itself: it is a line-by-line scalar port of phoboslab's qoi.h (64-entry colour hash, run, diff, luma and literal ops). It adds overhead the reference avoids: encode zero-fills a worst-case (channels+1) bytes-per-pixel std::vector, then calls shrink_to_fit (a second allocation and copy), and both loops branch on the channel count for every pixel. Nothing in it compares with qoixx's AVX2/NEON/SVE encoder or table-driven decoder.

## Compared with alternatives

Hard to justify: pick qoixx (C++20, SIMD encoder, published 1.4-1.7x over qoi.h) for speed, phoboslab/qoi (qoi.h) for portability, maintenance and input validation, or qoi-rust/rapid-qoi in Rust; libqoi only if C++14 plus a std::vector API is a hard requirement and inputs are trusted.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake) or source-drop of include/qoi/qoi.hpp and src/qoi.cpp |
| **Dependencies** | none for the two library files; the CMake project requires Conan packages fmt 8.0.1, libpng 1.6.37, catch2 2.13.7 and stb at configure time for its tests |
| **Minimum toolchain** | C++14 (CMAKE_CXX_STANDARD 14); CMake 3.4+ for the project build |
| **Platforms** | any (portable scalar C++) |
| **Thread safety** | Not documented; the functions keep no global state, so separate calls on separate buffers are independent (from reading the code). |
| **Drop-in for the baseline** | partial: same QOI bitstream as qoixx and qoi.h (the test encodes dice.png byte-identically to the reference dice.qoi), but a different C++ API |

## Gotchas

- decode() does not call is_valid() and does not check the header: inputs shorter than 14 bytes are read out of bounds in get_header, and inputs shorter than 8 bytes make size() - 8 wrap and read past the buffer. Call is_valid() first, but it checks only the magic and the 8-byte end marker, not channels or dimensions.
- The QOI_HEADER_ONLY switch includes qoi.cpp inside namespace qoi, and qoi.cpp reopens namespace qoi and includes &lt;iostream&gt; there, so the header-only mode looks unusable as written (definitions land in qoi::qoi); compile src/qoi.cpp as a normal source (from code reading, not built).
- The only fuzz target (tests/qoi_fuzz.cpp) fuzzes get_header alone, accepting inputs from 4 bytes, and ASAN is off in Config.cmake; decode() has never been fuzzed.
- tests/benchmark.cpp, commented out of the build, is a Catch2 template (Fibonacci cases) whose only codec case passes dice.png, a PNG file, to qoi::decode; its PNG signature parses as width 218,765,834, height 13 and 73 channels, so it would request about 207.6 GB and throw. No working benchmark exists in the repo.

## Known shortcomings

- The only speed numbers are issue #1's informal 20% encode and 30% decode over qoixx on an i7-10875H with no harness; the ROS PRs #103 and #104 name libqoi (30 against 3 fps versus PNG, 28% against 13% CPU) but #103 closed unmerged and #104 is open. Abandoned since 2022-09.
- Enricher (e120, 2026-10-05): the repo's tests/benchmark.cpp is commented out of the build, uses a Fibonacci placeholder template and feeds dice.png (a PNG) to qoi::decode (parses as 218,765,834 x 13 x 73 channels, about 207.6 GB), so nothing was ever timed with it; the code is a scalar qoi.h port with a zero-filled worst-case buffer and a shrink_to_fit copy, so the issue #1 '20-30% faster than qoixx' remark is implausible (qoixx itself reports 1.4-1.7x over qoi.h). Retiered C to D (retier-36). Security: no run-length bound check in decode (heap overflow up to 61 pixels on crafted input), 1- or 2-channel overrun by 2 bytes, get_header out-of-bounds read under 14 bytes, 32-bit size math with no pixel cap, QOI_HEADER_ONLY apparently broken, fuzz target covers get_header only with ASAN off.

## Caveats and trade-offs

One informal third-party comment: no benchmark code, compiler, flags, qoixx version, image content or repeat counts, and the stream is a live webcam so the numbers are end-to-end in a ROS node. The ROS PR #103 and #104 texts do name libqoi ('Dimitri Belopopsky's (@ShadowMitia) MIT Licensed library (https://github.com/ShadowMitia/libqoi)') as the library behind the 28%/13% CPU and 30 fps versus PNG's 3 fps figures, but those are CPU-load and frame-rate observations of a ROS transport plugin, not a throughput benchmark, and the PNG settings (compression level, encoder library) are not given; the PRs also quote the QOI format's general '20x-50x faster encoding and 3x-4x faster decoding' than PNG, which belongs to the format, not to this library. Neither PR was merged. No benchmark in the repo (tools/ holds only unix_compile.func). README calls it work in progress with expected API breaks. Last commit 2022-09-07. [retier] One informal third-party comment with no benchmark code, compiler, flags, qoixx version, image content or repeat counts. The repo's tests/benchmark.cpp is commented out of the build, uses a Fibonacci placeholder template, and its only decode case feeds dice.png (a PNG) to qoi::decode, which parses as a 218,765,834 x 13 x 73-channel image and asks for about 207.6 GB. Security: decode has no run-length bound check (heap overflow of up to 61 pixels on crafted input, relevant to the ROS network use), 1- or 2-channel decode overruns by 2 bytes, get_header reads out of bounds on inputs under 14 bytes, sizes use 32-bit arithmetic with no pixel cap; QOI_HEADER_ONLY appears broken (code reading); the fuzz target covers get_header only with ASAN off. Neither ROS PR was merged. README calls it work in progress. Last commit 2022-09-07.

README: work in progress, compliant with QOI v1.0, based on the phoboslab reference implementation; expect API breaks. Only 5 commits.

## Maintenance

Abandoned since 2022-09-07 (5 commits, README says work in progress); MIT and tiny enough to vendor, but the decoder needs bounds checks before it can be used on untrusted data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** Issue #1 is a single informal comment (awesomebytes, 2022-07-24) giving 'about 20%' encode and 'about 30%' decode over qoixx on an i7-10875H, with no benchmark code, compiler, flags, qoixx version or repeat counts, and the repo has no benchmark; numbers without methodology are C.
- **Retiered** C to D: Lowered C to D. Enricher e120 (2026-10-05) found the only harness in the repo, tests/benchmark.cpp: it is commented out of the build, its template is a Fibonacci placeholder, and its single decode case feeds dice.png (a PNG) to qoi::decode, which parses as width 218,765,834, height 13, 73 channels and requests about 207.6 GB, so nothing meaningful was ever timed with it. The code is a scalar port of qoi.h with a zero-filled worst-case buffer and a shrink_to_fit copy, while qoixx's own README shows 1.4-1.7x over qoi.h, so the 'about 20% encode / 30% decode faster than qoixx' remark in issue #1 (no code, compiler, flags, qoixx version or repeat counts, from a live webcam ROS node) is implausible from the code. Directional remark without methodology: D.
- **Verifier notes:** Record accurate apart from the claim that the ROS PR does not name its QOI library: PRs #103 and #104 both name libqoi, which adds a PNG-transport observation (30 vs 3 fps) to claimed_speedup but no methodology, so it stays C. Abandoned (last commit 2022-09-07, over 3 years).
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** informal third-party remark (issue #1)
- **Pages the verifier opened:**
  - <https://github.com/ShadowMitia/libqoi/issues/1>
  - <https://github.com/ShadowMitia/libqoi>
  - <https://github.com/ShadowMitia/libqoi/commits>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/LICENSE>
  - <https://github.com/ros-perception/image_transport_plugins/pull/103>
  - <https://github.com/ros-perception/image_transport_plugins/pull/104>
- **Sources the enricher read:**
  - <https://github.com/ShadowMitia/libqoi>
  - <https://github.com/ShadowMitia/libqoi/tree/main/include/qoi>
  - <https://github.com/ShadowMitia/libqoi/tree/main/src>
  - <https://github.com/ShadowMitia/libqoi/tree/main/tests>
  - <https://github.com/ShadowMitia/libqoi/issues/1>
  - <https://github.com/ShadowMitia/libqoi/issues?q=is%3Aissue+OR+is%3Apr>
  - <https://github.com/ShadowMitia/libqoi/commits/main>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/Config.cmake>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/unix_compile.config>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/cmake/flags.cmake>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/cmake/load_config.cmake>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/include/qoi/qoi.hpp>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/src/qoi.cpp>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/tests/benchmark.cpp>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/tests/qoi_tests.cpp>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/tests/qoi_fuzz.cpp>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/tests/catch.cpp>
  - <https://raw.githubusercontent.com/ShadowMitia/libqoi/HEAD/tests/qoi_test_images/dice.png>
  - <https://github.com/ros-perception/image_transport_plugins/pull/104>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/shadowmitia/libqoi`) · [data/wave10/enrich/raw/github_com_shadowmitia_libqoi.json](../../../data/wave10/enrich/raw/github_com_shadowmitia_libqoi.json) (enrichment confidence 0.8)

</details>
