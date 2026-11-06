"""Collect source-linked HSC exams. No guessed URLs or inferred question marks."""
import concurrent.futures, hashlib, json, re, sys, traceback
from pathlib import Path
from urllib.parse import urljoin, unquote
from harvest import ROOT, fetch, inspect
from pypdf import PdfReader

SUBJECTS=['Physics','Chemistry','Mathematics & Statistics','English','Computer Science I','Computer Science II']
def subject(s):
    if re.search('computer|compute.science',s,re.I): return 'Computer Science II' if re.search('paper.?2|p_ii|science.ii',s,re.I) else 'Computer Science I'
    for pat,name in [('physics','Physics'),('chemistry','Chemistry'),('math','Mathematics & Statistics'),('english','English')]:
        if re.search(pat,s,re.I): return name

def candidate(url, source, title=''):
    s=unquote(url); sub=subject(s+' '+title)
    if not sub or re.search(r'oct|july|jully|june|model|solution|sample|first.unit|1.sem',s+' '+title,re.I): return
    years=re.findall(r'20(?:0[7-9]|1\d|2[0-6])',s)
    if not years: return
    year=int(years[-1]); ident=hashlib.sha256(url.encode()).hexdigest()[:12]
    return {'id':ident,'year':year,'subject':sub,'set':title or unquote(url.split('/')[-1]),'session':'Main','medium':'English','status':'linked','source':source,'pdfUrl':url,'analysisStatus':'pending'}

def download(row):
    try:
        p=fetch(row['pdfUrl'],'papers','.pdf'); raw=p.read_bytes()
        if not raw.startswith(b'%PDF'): raise ValueError('Response is not a PDF')
        reader=PdfReader(p)
        try:
            pages=[page.extract_text(extraction_mode='plain') for page in reader.pages]
        except Exception:
            pages=['' for page in reader.pages]
        text='\n'.join(f'\n--- PAGE {i+1} ---\n{t}' for i,t in enumerate(pages))
        tp=ROOT/'sources'/'text'/(row['id']+'.txt');tp.write_text(text)
        row.update(status='downloaded',localPdf=str(p.relative_to(ROOT)),textPath=str(tp.relative_to(ROOT)),pages=len(pages),textCharacters=len(text),sha256=hashlib.sha256(raw).hexdigest())
        if len(text)<250: row['analysisStatus']='needs OCR'
    except Exception as e: row.update(status='download failed',error=str(e)[:200])
    return row

def main():
    archives=json.loads((ROOT/'sources'/'archives.json').read_text()); candidates=[]
    for a in archives:
        if 'isquareit' in a['url']:
            for l in a['links']:
                if re.search(r'hsc.*\.pdf',l['href'],re.I):
                    r=candidate(l['href'],a['url'],l['text'])
                    if r:candidates.append(r)
    byjus=json.loads((ROOT/'sources'/'byjus.json').read_text())
    for l in byjus['links']:
        if '.pdf' in l['href']:
            r=candidate(l['href'],byjus['url'],l['text'])
            if r:candidates.append(r)
    js=(ROOT/'sources'/'pages'/'390142dcd9b48c7a.html').read_text()
    for path in re.findall(r'"(assets/DATA/[^"\n]+\.pdf)"',js):
        r=candidate(urljoin('https://hscexam.vercel.app/',path),'https://hscexam.vercel.app/')
        if r:candidates.append(r)
    # Omtex posts contain actual named paper/PDF download links.
    for a in archives:
        if 'omtex' not in a['url']:continue
        for l in a['links']:
            if '.pdf' in l['href']:
                r=candidate(l['href'],a['url'],l['text'])
                if r:candidates.append(r)
    candidates=list({r['pdfUrl']:r for r in candidates}.values())
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for r in pool.map(download,candidates):
            rows.append(r);(ROOT/'sources'/'downloads.json').write_text(json.dumps(rows,indent=2))
            (ROOT/'data'/'papers.json').write_text(json.dumps(rows,indent=2))
            print(r['year'],r['subject'],r['status'],r.get('pages'),r.get('textCharacters'),r.get('error',''),flush=True)
    print('Downloaded',sum(r['status']=='downloaded' for r in rows),'of',len(rows))
if __name__=='__main__': main()
