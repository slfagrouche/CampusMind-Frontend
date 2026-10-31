"""CampusMind Policy Lab: deterministic, synthetic policy simulation (Python 3.10+)."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def tokens(text):
    return re.findall(r'[a-z]{2,}', text.lower())

class KnowledgeBase:
    def __init__(self, path=ROOT / 'sources.json'):
        self.sources = json.loads(Path(path).read_text())
        self.fingerprint = digest(self.sources)

    def search(self, query, jurisdiction, limit=3):
        if jurisdiction not in {'US', 'UAE'}:
            return []
        docs = [s for s in self.sources if s['jurisdiction'] in (jurisdiction, 'GLOBAL')]
        counts = [Counter(tokens(s['summary'] + ' ' + s['title'])) for s in docs]
        q = Counter(tokens(query))
        vocabulary = set(q).union(*(set(c) for c in counts))
        idf = {t: math.log((1 + len(docs)) / (1 + sum(t in c for c in counts))) + 1 for t in vocabulary}
        def vector(c):
            return {t: n * idf[t] for t, n in c.items()}
        def norm(v):
            return math.sqrt(sum(x*x for x in v.values()))
        qv = vector(q)
        ranked = []
        for doc, count in zip(docs, counts):
            v = vector(count)
            score = sum(qv.get(t, 0)*x for t, x in v.items()) / (norm(qv)*norm(v) or 1)
            if score > 0:
                ranked.append({**doc, 'score': round(score, 6)})
        return sorted(ranked, key=lambda d: (-d['score'], d['id']))[:limit]

# These are deliberately conservative sandbox rules, not a legal interpretation engine.
SCHEMA = {'jurisdiction': {'US', 'UAE', 'UNKNOWN'}, 'records': bool,
          'vendor_approved': bool, 'secondary_use': bool, 'withdrawn': bool}

class Sandbox:
    def __init__(self, kb=None):
        self.kb = kb or KnowledgeBase()
        self.state = {'jurisdiction': 'UNKNOWN', 'records': False,
                      'vendor_approved': False, 'secondary_use': False, 'withdrawn': False}
        self.log = []

    def step(self, event):
        if set(event) != {'id', 'facts', 'query'}:
            raise ValueError('Expected id, facts, query only')
        if not isinstance(event['id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', event['id']):
            raise ValueError('Invalid event id')
        if any(r['event_id'] == event['id'] for r in self.log):
            raise ValueError('Duplicate event id')
        if not isinstance(event['query'], str) or len(event['query']) > 2000:
            raise ValueError('Invalid query')
        if not isinstance(event['facts'], dict):
            raise ValueError('Facts must be an object')
        for key, value in event['facts'].items():
            rule = SCHEMA.get(key)
            if rule is None or (rule is bool and type(value) is not bool) or (isinstance(rule, set) and (not isinstance(value, str) or value not in rule)):
                raise ValueError('Invalid fact: ' + key)
        state = {**self.state, **event['facts']}
        evidence = self.kb.search(event['query'], state['jurisdiction'])
        reasons = []
        if state['jurisdiction'] == 'UNKNOWN': reasons.append('unknown_jurisdiction')
        if not evidence: reasons.append('no_matching_evidence')
        if state['records']:
            reasons.append('student_records_require_review')
            if not state['vendor_approved']: reasons.append('vendor_not_approved')
            if state['secondary_use']: reasons.append('secondary_use_requested')
            if state['withdrawn']: reasons.append('withdrawal_requires_review')
        pause = state['records'] and (not state['vendor_approved'] or state['secondary_use'] or state['withdrawn'])
        status = 'pause_data_use' if pause else ('human_review' if reasons else 'informational_only')
        # Each reviewer receives only the facts needed for its role. No personal records or query text are logged.
        review = {'service': {'scope': 'public_information' if not state['records'] else 'records_request'},
                  'privacy': {'status': status, 'reason_codes': reasons},
                  'evidence': {'citation_ids': [s['id'] for s in evidence]}}
        entry = {'sequence': len(self.log)+1, 'event_id': event['id'], 'state': state,
                 'review': review, 'status': status, 'source_digest': self.kb.fingerprint,
                 'previous_hash': self.log[-1]['hash'] if self.log else '0'*64}
        entry['hash'] = digest(entry)
        self.state = state
        self.log.append(entry)
        return json.loads(json.dumps(entry))

def verify(log, expected_head=None):
    previous = '0'*64
    for i, row in enumerate(log, 1):
        body = {k:v for k,v in row.items() if k != 'hash'}
        if row.get('sequence') != i or row.get('previous_hash') != previous or row.get('hash') != digest(body):
            return False
        previous = row['hash']
    return expected_head is None or previous == expected_head

DEMO = [
 {'id':'public', 'facts':{'jurisdiction':'UAE'}, 'query':'education learner privacy human agency'},
 {'id':'records', 'facts':{'records':True}, 'query':'student personal data consent protection'},
 {'id':'approved', 'facts':{'vendor_approved':True}, 'query':'personal data rights consent'},
 {'id':'reuse', 'facts':{'secondary_use':True}, 'query':'learner data privacy purpose'},
 {'id':'withdrawal', 'facts':{'withdrawn':True}, 'query':'personal data withdrawal consent rights'}]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', type=Path, help='Synthetic JSON events; never real student records')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    sandbox = Sandbox()
    events = json.loads(args.events.read_text()) if args.events else DEMO
    for event in events: sandbox.step(event)
    result = json.dumps({'mode':'deterministic_synthetic', 'log':sandbox.log,
                         'head_hash':sandbox.log[-1]['hash'] if sandbox.log else '0'*64,
                         'verified':verify(sandbox.log)}, indent=2)
    if args.output: args.output.write_text(result + '\n')
    else: print(result)
