# Benchmark evidence receipt

Data: synthetic_demonstration.

Complete paired observations admitted and exact McNemar/Holm analysis replayed.

Baseline: synthetic-parser-v1.
Pass rule: Synthetic fixture only&#58; output equals the case expected value exactly.

Cases: 3. Baseline passes: 1. Planned family: 2. Alpha: 0.05.

| Candidate | Passes | Wins | Losses | Effect (percentage points) | Holm p (exact) | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| synthetic-fast-v1 | 2 | 1 | 0 | 33.333333333333336 | 1/1 | No rejection; equivalence not established |
| synthetic-careful-v1 | 3 | 2 | 0 | 66.66666666666667 | 1/1 | No rejection; equivalence not established |

## Retained pins and byte identity

- Pre-outcome seal: `0d18499d7dcb9150785724d7121ffeafa8607ace1612900920b715c4f85b3947`
- Plan: `13d5c3882c0082a7c603ad464645f312f6ebe6bee4622cc9f4c35710e8086f8e`
- Handoff receipt: `a48b052b69deb57fe5919d28cbc0ea5d33c65fcf69befaba3dfab2c8d4d0594d`
- Raw pack: `7dbfa62198b0d1f5a32d2f77fc2de524e19600f2379c06e25a966a67b5162189`
- Raw observations: `3ee1c2e479379e624def23b5e5f8f960ecac7b8bd4c9c38f24154c35ce9fa691`
- Admitted CSV: `3ee1c2e479379e624def23b5e5f8f960ecac7b8bd4c9c38f24154c35ce9fa691`

## Bound assets

| Kind | ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| cases | empty | 27 | c9e67b313441f60496f263c828e51023a55fe999c627a68a5e28ea578774c87f |
| cases | unicode | 29 | f1349ecdd94ff8052b60268dbbde5f7fa357e23765fe729a754af3dc31ef10f0 |
| cases | truncated | 31 | aecbd64168e41759b407eae8205c65ff044d97a09b9574eafc3e9e466b7cadc2 |
| systems | synthetic-parser-v1 | 48 | 90665a73564fad9940461d345388b9e8cd35b655f3a9dd5509c18f1b55e7b39a |
| systems | synthetic-fast-v1 | 46 | f34a57cb3207c11ebaf7b5f1e3d03139296cb6a76b66b1c5d2723ca6ef7022a6 |
| systems | synthetic-careful-v1 | 49 | 9cbe4fc623d1cabfe6b18d00df52a7514918cdf92face52f00f36328418ba45e |

## Limits

The pre-outcome seal must be independently retained before collection. The receipt pin is retained at handoff; it does not preregister outcomes.

This receipt verifies consistency and recomputation, not honest scoring, execution of the sealed code, complete dependencies, case independence, representativeness, or the absence of repeated looks. A non-rejection is not equivalence. Practical value is not established.

The embedded pack and observations are unredacted. Markdown is a reading aid; use the JSON receipt and original independent pins for replay. Engine hashes identify code, not trusted authorship.
