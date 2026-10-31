# CampusMind Policy Lab

A small, reproducible **policy-simulation baseline** for the AI for Good UAE hackathon. It explores when an education assistant should stop and request human review as new facts arrive. Built with AI assistance, October 2026; independent project of Said Lfagrouche. This folder is separate from the existing CampusMind frontend and is not wired into its backend.

## Run

Python 3.10+, standard library only; no API key, installation, network call or student data required.

```sh
python policy-lab/lab.py
python policy-lab/lab.py --output policy-lab/demo-results.json
python -m unittest discover -s policy-lab -v
```

The demo supplies five synthetic events one at a time: public information, student-record request, vendor approval, secondary use, and withdrawal. Each result includes the current facts, review status, citation IDs and a hash chain. Queries are not logged. No disclosure or real educational decision is performed.

## Implemented

- TF-IDF/cosine retrieval over a three-document, manually curated source manifest.
- Explicit US/UAE filtering with global guidance; unsupported jurisdiction abstains.
- Separate service, evidence and privacy review outputs coordinated by deterministic Python rules.
- Typed event validation before any state mutation, duplicate event rejection, and structured reason codes.
- SHA-256 chain and optional externally saved head for detecting edits/truncation.
- Ten regression tests and an executable five-stage demo.

## Limits and next work

This baseline has **no LLM inference and no autonomous multi-agent execution**. Review roles are ordinary functions, not independent agents. These ten developer-authored tests are not a benchmark of legal correctness or model safety. No deployed users, live integrations or measured educational outcomes are claimed.

The source excerpts are short paraphrases, not a comprehensive policy corpus. A source hash identifies the bundled manifest, not the authenticity/freshness of a remote webpage. Rule decisions are conservative project choices, not a legal opinion. An approved vendor does not establish lawful disclosure. The audit chain is not signed and can be rewritten by an attacker who controls the log and saved head. Do not use real student information.

Next: domain-expert review of jurisdiction-specific scenarios, an optional local model for evidence-grounded explanations, independently authored challenge cases, and an authenticated human-review UI. Any model output must remain advisory and cannot change the rule decision.

See [technical report](TECHNICAL_REPORT.md), [source manifest](sources.json), and [demo results](demo-results.json).
