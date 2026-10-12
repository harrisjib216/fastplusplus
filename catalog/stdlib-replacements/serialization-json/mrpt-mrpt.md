# mrpt-serialization

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> MRPT's portable, versioned binary archive (CArchive); via the gtsam2mrpt_serial bridge it serializes GTSAM factor graphs about 2x faster than Boost.

| | |
|---|---|
| **Beats** | Boost.Serialization binary archive (GTSAM's gtsam::serializeToBinaryStream / deserializeFromBinaryStream) |
| **Claimed result** | README of MRPT/gtsam2mrpt_serial claims 'approximately 2x faster serialization and deserialization for mid-sized factor graphs'. Its own plots (docs/profiling-ser.png, docs/profiling-deser.png; bars read approximately from a log axis, derived from page data) show serialization about 1.7-2.2x faster for 56 to 22001 factors (about 3.7x at 12 factors), but deserialization only about 1.0-1.2x from 276 to 22001 factors (parity at 1101 factors), about 1.5x at 56 and about 2.7x at 12. The 2x deserialization claim for mid-sized graphs is overstated. |
| **Workload** | Serialize and deserialize a gtsam::Values plus gtsam::NonlinearFactorGraph (Pose/Point/Rot values, Prior and Between factors with noise models) through mrpt::serialization archives versus GTSAM's Boost binary archive, graph sizes N = 1, 5, 25, 100, 500, 2000, results on a log time axis. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700HQ @ 2.60 GHz, Ubuntu 20.04, Boost 1.71, MRPT 2.4.4 |
| **Adoption** | 2.2k stars (mrpt/mrpt); 7 stars (gtsam2mrpt_serial); packaged for ROS 2 Humble to Rolling |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/mrpt/mrpt) · [benchmark](https://github.com/MRPT/gtsam2mrpt_serial) |

## Verdict

First-party plots (MRPT 2.4.4, Boost 1.71, Ubuntu 20.04, Intel Core i7-6700HQ, compiler and build type not stated) compare gtsam2mrpt_serial over in-memory CMemoryStream against GTSAM's Boost binary archive into std::stringstream for graphs of 12 to 22001 factors: serialization is about 1.7-2.2x faster from 56 factors up, deserialization about 1.0-1.2x from 276 factors up (derived from page data, log-axis bar reading); only the 12-factor point reaches 2.7-3.7x, partly from Boost archive construction inside the timer.

## Use it when

- You already use GTSAM with MRPT (for example in MOLA or a ROS 2 SLAM stack) and want to save or send factor graphs and Values about 2x faster to write than GTSAM's Boost binary archive.
- You need a binary format that stays readable across endianness, word size and OS, which Boost binary archives do not guarantee.
- Graphs built only from Pose2/Pose3/Point2/Point3/Rot2/Rot3 values with PriorFactor and BetweenFactor and the standard noise models (including robust m-estimators).
- You want transparent gzip or zstd compression or socket transport through mrpt-io streams without extra glue code.
- Projects on GTSAM 4.3+, which dropped Boost and therefore its built-in serialization, where the bridge is one of few ready-made binary formats.

## Skip it when

- Read-heavy workloads: the published plot shows deserialization at parity with Boost for about 276 to 22001 factors (1.0-1.2x), not the README's 2x.
- Graphs with any other factor type (projection, IMU, smart, custom factors) or value type (calibrations, NavState, vectors): the bridge throws 'Serialization not implemented'.
- Generic C++ object serialization unrelated to GTSAM or MRPT types: you would have to write per-class code against CArchive, and general serializers in the catalog are faster and documented with stronger evidence.
- Workloads that rely on deserialized factors sharing one noise-model object: the bridge recreates a separate noise model per factor, while Boost restores the shared_ptr aliasing.
- Projects that cannot take MRPT 3.x (the bridge requires MRPT &gt;= 3.0 and mola_common's CMake helpers; RHEL builds are not available on ROS 2 Humble).

## How it is fast

CArchive writes each primitive as a raw little-endian memcpy into the stream (byte swapping only on big-endian hosts), with no object tracking, no pointer registry and no per-archive header. The GTSAM bridge dispatches each value, factor and noise model by dynamic_cast and writes a short string type tag plus the raw doubles, avoiding Boost's polymorphic-pointer machinery (BOOST_CLASS_EXPORT GUID lookup, class-id tables and shared_ptr tracking). The output stream is a plain realloc-grown buffer (CMemoryStream, 4 KB growth steps) in the benchmark.

## Compared with alternatives

Pick it over HPS, zpp::bits or Cap'n Proto only when the objects are GTSAM factor graphs and you are already on MRPT: it is the only catalogued option with ready-made GTSAM support and an endian-stable, versioned format, while HPS (also measured against Boost.Serialization) and zpp::bits are general-purpose and have stronger, generic benchmarks.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | mrpt_serialization (needs mrpt_common, mrpt_rtti; jsoncpp optional for its JSON/YAML scheme archives); the GTSAM bridge also needs mrpt_io, mrpt_math, mrpt_poses, mrpt_random, mola_common (CMake macros) and GTSAM 4.2 (Boost) or &gt;= 4.3 |
| **Minimum toolchain** | C++17, CMake 3.16 (mrpt_serialization) / 3.10 (gtsam2mrpt_serial); MRPT &gt;= 3.0 for the bridge |
| **Platforms** | Linux on x86_64 and arm64 (ROS 2 build farm: Ubuntu, RHEL 9/10 x86_64, Fedora); MRPT also ships Windows builds; little- and big-endian hosts handled by MRPT_IS_BIG_ENDIAN conversions |
| **Thread safety** | not documented; a CArchive is a stateful wrapper around one stream, so use one archive per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the numbers: tests/main.cpp times gtsam::serializeToBinaryStream / deserializeFromBinaryStream, which construct a boost binary_oarchive / binary_iarchive (header write or read) inside the timed region twice per repetition, while the MRPT archive is created before the CTimeLoggerEntry starts; this inflates the small-graph ratios (about 3.7x serialize and 2.7x deserialize at 12 factors).
- Deserialization is the weak side by construction: deserialize_factor builds a throwaway gtsam::Values per factor to decode one value, compares the type tag against a chain of std::string literals, and allocates a fresh noise model per factor (sharing is lost), which matches the near-parity deserialization plot.
- Pose3 and Rot3 are stored as yaw/pitch/roll Euler angles via mrpt::math::TPose3D and rebuilt from a rotation matrix, so round trips are approximate (the tests compare with GTSAM's equals() tolerance), not bit-exact; Boost stores the 9 rotation-matrix entries (or the quaternion with GTSAM_USE_QUATERNIONS), so the two timed paths do different work per rotation (trig conversion and 3 doubles vs 9 copied doubles).
- The 2026-09-25 release (0.4.0) fixed noise-model serialization bugs (Constrained models dropped their sigmas, null m-estimators wrote a corrupt stream, unknown m-estimators were not rejected, factors with more than 65535 keys were mis-written); the 2022 benchmark graph used only isotropic models, so those paths were not timed, but older files with mixed Constrained models lost data.

## Known shortcomings

- Downgraded claim (tier C): plots show about 1.0-1.2x faster deserialization for 276-22001 factors (parity at 1101) and about 1.7-2.2x serialization vs Boost binary archive; the Boost archive is built inside the timer while the MRPT archive is built outside; plots are stale (2022-04-19, MRPT 2.4.4, 11N+1 factors vs the current generator's 12N+1); compiler and flags unstated; the measured artefact is MRPT/gtsam2mrpt_serial (7 stars), not mrpt core.
- Enricher (gtsam2mrpt_serial tests/main.cpp): the Boost binary_oarchive/iarchive is built inside the timer twice per repetition while the MRPT archive is built before CTimeLoggerEntry, inflating the small-graph ratios (3.7x serialize / 2.7x deserialize at 12 factors); deserialization parity is explained by deserialize_factor building throwaway gtsam::Values and a new noise model per factor (shared_ptr sharing lost); Pose3/Rot3 are stored as yaw/pitch/roll Euler angles (approximate round trip) while Boost stores 9 matrix doubles, so the paths do different work. 0.4.0 (2026-09-25) fixed noise-model bugs (Constrained sigmas dropped, null m-estimator corrupting the stream, more than 65535 keys); the 2022 timed graph used isotropic models only, so the timed paths are unaffected. No CMAKE_BUILD_TYPE default; plots stale (2022); the measured artefact is MRPT/gtsam2mrpt_serial, not mrpt core.

## Caveats and trade-offs

The benchmark is in a separate repo (MRPT/gtsam2mrpt_serial, same organisation, first-party) and measures a GTSAM bridge built on mrpt-serialization, not the core library on generic data; the baseline is Boost.Serialization through GTSAM, not protobuf, FlatBuffers or another widely used serializer. Deserialization is roughly at parity with Boost for mid-sized graphs despite the README's 2x claim; only serialization is about 2x. Harness asymmetry: gtsam::serializeToBinaryStream / deserializeFromBinaryStream construct a boost binary_oarchive/iarchive inside the timed region (twice per rep, for Values and graph), while the MRPT archive is constructed before the CTimeLoggerEntry starts, which inflates the small-graph ratios. The plots are stale: committed 2022-04-19 with MRPT 2.4.4, and their factor counts (12, 56, 276, 1101, 5501, 22001 = 11N+1) do not match the current tests/sampleData.cpp generator (12N+1 factors, robust noise models added since), so the published numbers were not produced by the current code; the repo now requires MRPT 3.0. Compiler, flags and build type are unstated; exact timings exist only as images. The profiling code only compiles when GTSAM uses Boost (GTSAM 4.2), uses mrpt::system::CTimeLogger with max(5, 1000/N) repetitions, and runs into in-memory streams (CMemoryStream vs std::stringstream). [retier] MRPT/gtsam2mrpt_serial plots (2022-04-19, MRPT 2.4.4, compiler and flags unstated, no CMAKE_BUILD_TYPE default): about 1.7-2.2x faster serialization and 1.0-1.2x deserialization vs Boost binary archive; Boost archive built inside the timer twice per repetition while the MRPT archive is built outside, inflating small-graph ratios. Deserialize rebuilds gtsam::Values and a noise model per factor; Pose3/Rot3 stored as Euler angles (approximate) vs Boost's 9 doubles, so the paths do different work. Measured artefact is gtsam2mrpt_serial (7 stars), not mrpt core; 0.4.0 fixed noise-model bugs outside the timed paths.

mrpt-serialization is a versioned, endian- and word-size-stable binary archive (mrpt::serialization::CArchive) driven by CSerializable class registration and stream operators, with optional gzip or zstd streams via mrpt-io; it is not schema-based like protobuf, and the faster path in the benchmark needs the gtsam2mrpt_serial bridge library plus MRPT 3.x.

## Maintenance

MRPT is actively maintained (BSD-3-Clause, ROS 2 Humble to Rolling packages) and the bridge had releases 0.3.0 and 0.4.0 in September 2026, but the benchmark plots date from 2022-04-19 and were not regenerated: the current generator makes 12N+1 factors with robust noise models instead of the plotted 11N+1, the profiling code compiles only against Boost-based GTSAM 4.2, the project sets no default CMAKE_BUILD_TYPE, and the byte sizes the harness records are not published.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark in the same organisation's MRPT/gtsam2mrpt_serial repo (code public at tests/main.cpp, testSerializeProfiler, CPU i7-6700HQ stated) but compiler, flags and build type are not stated anywhere, so it cannot reach A; results exist only as two log-scale PNG plots committed 2022-04-19.
- **Verifier notes:** README quotes match the page, but reading the deserialization plot shows near parity (about 1.0-1.2x) for 276-22001 factors, so the claim is overstated; tier stays C. The measured artifact is MRPT/gtsam2mrpt_serial (7 stars, BSD-3-Clause), not mrpt/mrpt core; consider a repo_url override or naming the entry gtsam2mrpt_serial. Metadata checked: mrpt/mrpt 2.2k stars, BSD-3-Clause, not archived or a fork, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/README.md>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/main.cpp>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/sampleData.cpp>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/sampleData.h>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/docs/profiling-ser.png>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/docs/profiling-deser.png>
  - <https://github.com/MRPT/gtsam2mrpt_serial>
  - <https://github.com/MRPT/gtsam2mrpt_serial/commits/HEAD/docs>
  - <https://raw.githubusercontent.com/borglab/gtsam/4.2/gtsam/base/serialization.h>
  - <https://github.com/mrpt/mrpt>
  - <https://github.com/mrpt/mrpt/commits/develop>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/README.md>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/main.cpp>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/sampleData.cpp>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/sampleData.h>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/tests/boost-exports.h>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/package.xml>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/CHANGELOG.rst>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/src/serialize.cpp>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/include/gtsam2mrpt_serial/serialize.h>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/include/gtsam2mrpt_serial/gtsam_detect_version.h>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/docs/profiling-ser.png>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/HEAD/docs/profiling-deser.png>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/2b2713fad591d9dd84fde0177d95b69d5733bbd7/gtsam2mrpt_serial/tests/main.cpp>
  - <https://raw.githubusercontent.com/MRPT/gtsam2mrpt_serial/2b2713fad591d9dd84fde0177d95b69d5733bbd7/CMakeLists.txt>
  - <https://github.com/MRPT/gtsam2mrpt_serial/tree/2b2713fad591d9dd84fde0177d95b69d5733bbd7>
  - <https://github.com/MRPT/gtsam2mrpt_serial/commits/develop>
  - <https://github.com/MRPT/gtsam2mrpt_serial/commit/386cff904c5b11ab85d827049c709153a4ff19a3>
  - <https://github.com/MRPT/gtsam2mrpt_serial/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/borglab/gtsam/4.2/gtsam/base/serialization.h>
  - <https://github.com/mrpt/mrpt>
  - <https://github.com/mrpt/mrpt/tree/develop>
  - <https://github.com/MRPT/mrpt/issues?q=is%3Aissue+serialization>
  - <https://raw.githubusercontent.com/MRPT/mrpt/develop/modules/mrpt_serialization/package.xml>
  - <https://raw.githubusercontent.com/MRPT/mrpt/develop/modules/mrpt_serialization/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MRPT/mrpt/develop/modules/mrpt_serialization/include/mrpt/serialization/CArchive.h>
  - <https://raw.githubusercontent.com/MRPT/mrpt/develop/modules/mrpt_io/include/mrpt/io/CMemoryStream.h>
  - <https://raw.githubusercontent.com/MRPT/mrpt/develop/modules/mrpt_io/src/CMemoryStream.cpp>
  - <https://raw.githubusercontent.com/borglab/gtsam/4.2/gtsam/geometry/Rot3.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mrpt/mrpt`) · [data/wave1/enrich/raw/github_com_mrpt_mrpt.json](../../../data/wave1/enrich/raw/github_com_mrpt_mrpt.json) (enrichment confidence 0.75)

</details>
