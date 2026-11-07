"""Prepare the private answer catalog; encrypt it separately before deployment.

Published solutions remain links to their publishers. Publisher answer text is
not republished. Plaintext output is always confined to ignored private/answers.
"""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'private/answers'
OUT.mkdir(parents=True,exist_ok=True)
papers=[p for p in json.loads((ROOT/'data/papers.json').read_text()) if p.get('localPdf') and not p.get('duplicateOf') and not p.get('excluded')]
references=json.loads((ROOT/'private/research/published-references.json').read_text())
reference_map={(r['subject'].replace('Mathematics and Statistics','Mathematics & Statistics'),r['year']):r for r in references}
extra={
 '7cab204ab871':('OMTEX Classes · Physics 2020 worked solutions','https://www.omtexclasses.com/2025/12/maharashtra-board-class-12-physics-question-paper-solution-february-2020.html'),
 'b69637d9ccb4':('OMTEX Classes · Chemistry 2020 worked solutions','https://www.omtexclasses.com/2026/01/maharashtra-board-hsc-chemistry-2020-solved-paper.html'),
 '946f6269c654':('OMTEX Classes · English 2020 Set B worked solutions','https://www.omtexclasses.com/2025/12/maharashtra-hsc-english-board-paper-2020-solutions-j301b.html'),
}
catalog=[]
for p in sorted(papers,key=lambda p:(-p['year'],p['subject'],p.get('part',0))):
 path=OUT/(p['id']+'.json')
 existing=json.loads(path.read_text()) if path.exists() else {}
 if existing.get('status') in ['original','partial']:
  entry=existing
 elif p['id'] in extra:
  title,url=extra[p['id']]
  entry={'status':'published','note':'Published solutions matched to this paper. Open the publisher’s answer page below. These are study solutions, not an official board marking scheme. External public pages remain public.','sources':[{'title':title,'url':url}],'references':[]}
 elif (p['subject'],p['year']) in reference_map:
  r=reference_map[(p['subject'],p['year'])]
  if not r['references'] or not all(c['present'] for c in r.get('sampleChecks',[])) or len(r.get('sampleChecks',[]))!=2:raise ValueError('Unverified source: '+r['url'])
  # Store question numbers and destination links, not the publisher’s question/answer prose.
  entry={'status':'published','note':'Published answer references matched to the question paper. First and last answer pages were checked; individual answers have not all been independently marked. Some references cover a grouped activity. External public pages remain public.','sources':[{'title':'Shaalaa · published solutions','url':r['url']}],'references':[{'question':a.get('question',''),'questionText':'Published solution','marks':a.get('marks',''),'url':a['url']} for a in r['references']]}
 else:
  entry={'status':'pending','note':'A complete published solution has not been verified for this paper. Original question-by-question answers are being prepared; this paper is not counted as answered yet.','sources':[],'answers':[]}
 entry.update({k:p.get(k) for k in ['id','subject','year','part']})
 entry['paperPdf']=p['localPdf']
 path.write_text(json.dumps(entry,ensure_ascii=False,indent=2))
 status=entry['status']
 labels={'published':'Published solution references','original':'Original worked answers','partial':'Partial worked answers','pending':'Answers in preparation'}
 coverage=(f"{len(entry.get('answers',[]))} worked question / subquestion answers" if status in ['original','partial'] else f"{len(entry.get('references',[]))} question-level references" if entry.get('references') else 'Published paper solution page' if status=='published' else 'No complete answer set yet')
 catalog.append({k:entry.get(k) for k in ['id','subject','year','part','status']}|{'label':labels[status],'coverage':coverage})
counts=Counter(p['status'] for p in catalog)
summary=f"{len(catalog)} collected papers: {counts['published']} with published solution references, {counts['original']} with original worked answers, {counts['partial']} partial sets, and {counts['pending']} still in preparation."
(OUT/'index.json').write_text(json.dumps({'summary':summary,'counts':dict(counts),'papers':catalog},ensure_ascii=False,indent=2))
print(summary)
