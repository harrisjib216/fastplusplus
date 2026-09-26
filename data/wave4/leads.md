# Wave 4 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records. Seed them (pipeline/seed.py) before wave 4 closes.

- cJSON (https://github.com/DaveGamble/cJSON): beats jsmn on 11 of 14 files and, per the simdjson VLDB 2019 paper (Table 10), nlohmann/json on most files. Found by the jsmn enricher.
- Colfer C output vs protobuf C++: recorded as a measurement on the Colfer entry (data/decisions.json); could become its own C entry if the id scheme allows one repo with two languages.
- Pison/JSONSki single-threaded variants and pikkr lineage: covered.
- bemayer/xml-benchmark (https://github.com/bemayer/xml-benchmark): independent, CI-run, monthly cross-language XML shootout (found by the yaml-toml-xml registry agent). Harvest its other C/C++ winners against libxml2/pugixml.
- flatcc (https://github.com/dvidelabs/flatcc): C FlatBuffers implementation; its benchmark doc claims about 10% faster encode than Google flatbuffers C++, decode tied (first-party, no compiler stated). Found by the binary-schemas blogs agent.
- zig-flatbuffers and lalinsky/msgpack.zig: Zig libraries that match or beat s2s on some fixtures of the third-party Zig serialization suite (found by the s2s enricher). Not catalogued.
