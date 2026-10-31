# CampusMind Policy Lab
AI for Good UAE - technical report draft - 31 October 2026

Team: CampusMind. Team leader and sole member: Said Lfagrouche.
Repository: https://github.com/slfagrouche/CampusMind-Frontend/tree/dubai-policy-lab/policy-lab
Status: working deterministic baseline; not yet a complete AI-agent submission.

## 1. Introduction
CampusMind Policy Lab asks a practical question: when an education assistant learns a new fact, can it explain why its next action must change? A helpful answer to a public-information question can become an inappropriate data-sharing action when a vendor asks for student records. The prototype makes these transitions observable and reproducible. Its contribution is an inspectable evaluation scaffold rather than a claim to automate legal compliance.

## 2. Use case
A synthetic university adviser begins with public educational guidance. A later event introduces personal-record processing, followed by vendor approval, secondary use and consent withdrawal. Events are presented sequentially; the decision component cannot inspect future events. Service, evidence and privacy review outputs expose distinct concerns, with a coordinator selecting informational_only, human_review or pause_data_use. No records are collected, transferred or used for decisions.

## 3. Requirements and implementation
Python 3.10+ runs offline without dependencies. A versioned source manifest contains government and UNESCO summaries with URLs, jurisdiction and source type. TF-IDF/cosine ranking selects evidence after jurisdiction filtering. The event interface accepts a limited schema of synthetic facts, validates the complete event before changing state, and rejects duplicate IDs. Unknown jurisdiction or no matching evidence causes human review. Personal-record requests never receive an automated approval. Deterministic controls are project-specific conservative rules; they are not extracted legal obligations.

Logs include sequential IDs, the current synthetic state, reason codes, citation IDs and the manifest digest. Query text is excluded. Each entry hashes its predecessor. An independently retained head is needed to detect truncation or full-chain replacement; signatures and trusted storage are future work. The current implementation uses simulated reviewer roles, not independent LLM agents.

## 4. Architecture and readiness mapping
Conceptual mapping to ITU-T Y.3172, not a conformance claim:

| Node | Prototype element |
| --- | --- |
| SRC | Synthetic event stream and source manifest |
| C | JSON loading and schema validation |
| PP | Tokenization and jurisdiction filtering |
| M | TF-IDF similarity model; no generative model |
| P | Conservative review rules |
| D | Coordinator assembling structured results |
| SINK | JSON evidence and audit output |

Selected AI Readiness 2.0 themes are operationalized as local checks: source provenance through manifest hashes; policy context through jurisdiction filters; human involvement through review statuses; reproducibility through offline execution. This is a design mapping, not a scored readiness assessment. Human review is currently a status, not a staffed workflow or approval interface.

## 5. Sequential error scenarios and evaluation
Five synthetic events produced these measured outputs on 31 October 2026:

| Stage | New fact | Output | Proposed human action |
| --- | --- | --- | --- |
| 1 | UAE public-guidance request | informational_only | Review cited guidance if needed |
| 2 | Student records requested; vendor unapproved | pause_data_use | Check purpose, authority and vendor |
| 3 | Vendor marked approved | human_review | Check remaining disclosure conditions |
| 4 | Secondary use requested | pause_data_use | Escalate purpose and contract review |
| 5 | Withdrawal received | pause_data_use | Determine applicable rights and obligations |

Ten unittest cases passed: staged outputs/no future-fact leakage; unknown jurisdiction; jurisdiction exclusion; absent evidence; query-text instructions cannot modify structured rules; atomic invalid-fact rejection; duplicate IDs; log edit/truncation detection with a saved head; detached return values; and relevant-source ranking. Run `python -m unittest discover -s policy-lab -v` to reproduce. This is a small developer-authored regression suite, not an independent adversarial benchmark. No accuracy, adoption, latency benefit or real-world safety claim is supported by these results.

## 6. Policy and standards gaps
The corpus is too small for deployment and omits many exceptions, local rules and institution-specific contracts. FERPA material is restricted to the US profile; it is not treated as UAE law. UNESCO guidance is nonbinding. Data type, age, authority, emergency conditions and revocation scope require richer models and qualified review. Lexical retrieval can miss relevant passages and cannot resolve conflicting authority. The next phase requires expert-labeled cases, source freshness/version monitoring, accessible human-review interfaces and a measured optional local-LLM explanation component. Existing CampusMind frontend is background work, not evidence that this new module is deployed.

## References
1. ITU-T Y.3172 summary: https://www.itu.int/dms_pubrec/itu-t/rec/y/T-REC-Y.3172-201906-I!!SUM-HTM-E.htm
2. ITU AI Readiness 2.0: https://www.itu.int/dms_pub/itu-t/opb/ai4g/T-AI4G-AI4GOOD-2025-6-PDF-E.pdf
3. Government source URLs and UNESCO guidance are listed in sources.json.
