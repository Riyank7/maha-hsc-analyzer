"""Merge valid recoveries; retain all failed attempts in source audit logs only."""
import json,hashlib,re
from pathlib import Path
from harvest import ROOT
def main():
    rows=json.loads((ROOT/'data/papers.json').read_text());byid={p['id']:p for p in rows}
    for name in ['downloads','scan-papers','more-papers','cs-alternates','cs2-alternates','cs2025','cs1-2022-check','study-alternates','target-recoveries','cs2016-recoveries','shaalaa-recoveries']:
        f=ROOT/'sources'/f'{name}.json'
        if f.exists():
            for p in json.loads(f.read_text()):
                if p.get('localPdf') and p['id'] not in byid:byid[p['id']]=p
    rows=list(byid.values());seen={}
    for p in rows:
        h=p.get('sha256')
        if h and h in seen:p['duplicateOf']=seen[h]
        elif h:seen[h]=p['id']
        if p['year']<=2012 and p['subject'] in ['Physics','Chemistry','Mathematics & Statistics']:
            name=p.get('pdfUrl','').lower();m=re.search(r'(?:physics|chemistry|statistics)-(1|2)\.pdf',name)
            if m:p['part']=int(m[1]);p['set']='Paper '+('I' if p['part']==1 else 'II');p['metadataStatus']='archive-attributed';p['notes']='Year and main session attributed by the source archive; the retyped file does not print an exam date.'
    pairs={'76f282c9813e':'b45ca696cdd2','c3b2f2b60155':'7ac6ea6bd23c','4855f4e1c9d5':'ba4915db5bbd','07a4bf49648f':'2a533f39423c','a9a714475941':'b79134a43bfc','2187e01ed63a':'b79134a43bfc','e11ef9c75d50':'fe754e74bb6b'}
    for p in rows:
        if p['id'] in pairs and pairs[p['id']] in byid:p['duplicateOf']=pairs[p['id']]
    # Confirmed mislabeled / undated copies remain available in the audit trail.
    for p in rows:
        if p['id']=='9a9c525bc495':p.update(excluded=True,year=2008,session='October supplementary',exclusionReason='Labeled 2007 by archive; printed paper says October 2008.')
        if p['id']=='e11ef9c75d50':p.update(excluded=True,year=2020,exclusionReason='Cropped V-234 copy mislabeled 2022 by archive; verified against complete dated 2020 main paper.')
    (ROOT/'data/papers.json').write_text(json.dumps(rows,indent=2))
    jobs=[{'input':str(ROOT/p['localPdf']),'output':str(ROOT/'sources/text'/f"{p['id']}.ocr.txt")} for p in rows if p.get('localPdf') and not p.get('duplicateOf') and not p.get('excluded') and not (ROOT/'sources/text'/f"{p['id']}.ocr.txt").exists()]
    (ROOT/'sources/ocr-new.json').write_text(json.dumps(jobs))
    print(len(rows),'records;',len(jobs),'new OCR jobs')
if __name__=='__main__':main()
