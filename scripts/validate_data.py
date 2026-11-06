"""Validate the actual public corpus before deployment, including offered totals."""
import json,hashlib
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
papers=json.loads((ROOT/'data/papers.json').read_text());questions=json.loads((ROOT/'data/questions.json').read_text())
active=[p for p in papers if p.get('localPdf') and not p.get('duplicateOf') and not p.get('excluded')]
assert len({p['id'] for p in papers})==len(papers),'Duplicate paper identifiers'
assert len({p['sha256'] for p in active})==len(active),'Duplicate PDF bytes'
assert len({(q['paperId'],q['question']) for q in questions})==len(questions),'Duplicate question references'
totals=defaultdict(int)
for q in questions:
 assert q['marks']>0 and q.get('reviewed') and q['chapter'], 'Invalid reviewed mapping'
 totals[q['paperId']]+=q['marks']
for p in active:
 raw=(ROOT/p['localPdf']).read_bytes()
 assert raw.startswith(b'%PDF'),'Invalid PDF: '+p['id']
 assert hashlib.sha256(raw).hexdigest()==p['sha256'],'PDF hash mismatch: '+p['id']
 expected=p.get('requiredMarks') if p.get('analysisResolution')=='section' else p.get('offeredMarks')
 assert totals[p['id']]==expected, 'Marks mismatch: '+p['id']
print(f'Validated {len(active)} distinct PDFs and {len(questions)} mapping records')
