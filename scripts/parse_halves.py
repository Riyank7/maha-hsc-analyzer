import json,re
from pathlib import Path
from harvest import ROOT
from parse_legacy import parts
CONFIG=[('1',8,1),('2A',2,2),('2B',3,3),('3A',2,2),('3B',3,3),('4A',3,2),('4B',2,4),('5',3,4)]
def parse(p):
    f=ROOT/'sources/text'/f"{p['id']}.plain.txt";t=f.read_text() if f.exists() else ''
    if len(t)<1000:t=(ROOT/'sources/text'/f"{p['id']}.ocr.txt").read_text()
    t=re.sub(r'--- PAGE \d+ ---','',t);t=t.replace('( l)','(i)').replace('(1)','(i)')
    q=list(re.finditer(r'Q\.?\s*([1-5])\.?\s*(?=\(?[A-Z]|Select|Attempt)',t))
    out=[]
    for i,m in enumerate(q):
        num=m[1];body=t[m.end():q[i+1].start() if i+1<len(q) else len(t)]
        if num in ['1','5']:groups=[(num,body)]
        else:
            split=re.search(r'\(B\)',body)
            if not split:continue
            groups=[(num+'A',body[:split.start()]),(num+'B',body[split.end():])]
        for group,s in groups:
            _,count,marks=next(c for c in CONFIG if c[0]==group)
            pp=parts(s,count)
            for j,x in enumerate(pp,1):out.append({'paperId':p['id'],'question':group+f'.{j}','marks':marks,'text':x})
    return out
if __name__=='__main__':
    out=[]
    for p in json.loads((ROOT/'data/papers.json').read_text()):
        if p.get('duplicateOf') or p.get('excluded') or p['subject'] not in ['Physics','Chemistry'] or p['year']>2012:continue
        qs=parse(p);out+=qs
        print('\nPAPER',p['id'],p['year'],p['subject'],'items',len(qs),'marks',sum(q['marks'] for q in qs))
        for x in qs:print(x['question'],x['marks'],' '.join(x['text'].split())[:300])
    (ROOT/'sources/half-items.json').write_text(json.dumps(out,indent=2))
