import json,re
from pathlib import Path
from harvest import ROOT

def parts(text,expected):
    # Top-level roman items progress monotonically from i; ignore nested lists.
    nums=['i','ii','iii','iv','v','vi','vii','viii','ix','x'][:expected]
    positions=[];start=0
    for roman in nums:
        m=re.search(r'(?m)^\s*\(?'+roman+r'[.)]\s*',text[start:])
        if not m:return []
        pos=start+m.start();positions.append(pos);start=start+m.end()
    return [text[p:positions[i+1] if i+1<len(positions) else len(text)].strip() for i,p in enumerate(positions)]

def parse(p):
    path=ROOT/'sources/text'/f"{p['id']}.plain.txt"
    if not path.exists():return []
    t=path.read_text()
    if len(t)<1000 or p['id']=='a92405463d24':t=(ROOT/'sources/text'/f"{p['id']}.ocr.txt").read_text()
    t=re.sub(r'--- PAGE \d+ ---','',t)
    t=re.sub(r'(?m)^ii\s*\n\s*i\.', 'iii.',t)
    starts=list(re.finditer(r'Q\.\s*([1-8])\.',t));out=[]
    for j,m in enumerate(starts):
        num=int(m[1]);s=t[m.end():starts[j+1].start() if j+1<len(starts) else len(t)]
        head=re.sub(r'\s+','',s[:250]).lower()
        if 'select' in head and 'answer' in head:mark,expected=1,7
        elif 'anysix' in head:mark,expected=2,8
        elif 'anythree' in head:mark,expected=3,4
        else:mark,expected=7,2
        if mark==7:
            pp=parts(s,2) if 'anyone' in head else []
            if not pp:pp=re.split(r'\bOR\b',s)
        else:pp=parts(s,expected)
        pp=[x for x in pp if len(x.strip())>15]
        for k,x in enumerate(pp,1):out.append({'paperId':p['id'],'question':f'{num}.{k}' if mark!=7 or len(pp)>1 else f'{num}.alternative{sum(a["question"].startswith(str(num)) for a in out)+1}','marks':mark,'text':x})
    return out
if __name__=='__main__':
    papers=json.loads((ROOT/'data/papers.json').read_text());out=[]
    for p in papers:
        if p.get('duplicateOf') or p['subject'] not in ['Physics','Chemistry'] or not 2013<=p['year']<=2018:continue
        qs=parse(p);out+=qs
        print('\nPAPER',p['id'],p['year'],p['subject'],'items',len(qs),'marks',sum(q['marks'] for q in qs))
        for q in qs:
            s=' '.join(q['text'].split());s=re.split(r'\(?A\)',s)[0]
            print(q['question'],q['marks'],s[:650] if q['marks']==7 else s[:230])
    (ROOT/'sources/legacy-items.json').write_text(json.dumps(out,indent=2))
