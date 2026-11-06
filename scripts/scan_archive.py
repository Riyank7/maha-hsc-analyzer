"""Cache publicly visible page scans and assemble direct local PDFs."""
import concurrent.futures,hashlib,json,re
from html.parser import HTMLParser
from urllib.parse import unquote
from PIL import Image
from harvest import ROOT,fetch
from collect import subject

class Scans(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='img' and 'contentimg' in d.get('class',''):
            self.urls.append(d.get('data-src') or d.get('src'))

def get_paper(l):
    try:
        u=l['href'];year=int(re.search(r'/(20\d\d)/',u)[1]);sub=subject(unquote(u));ident=hashlib.sha256(u.encode()).hexdigest()[:12]
        p=fetch(u);h=Scans();h.feed(p.read_text());imgs=[]
        for url in h.urls:
            ip=fetch(url,'papers','.webp');imgs.append(Image.open(ip).convert('RGB'))
        if not imgs:raise ValueError('No visible paper scans')
        out=ROOT/'sources/papers'/f'{ident}.pdf'
        imgs[0].save(out,'PDF',save_all=True,append_images=imgs[1:],resolution=110)
        return {'id':ident,'year':year,'subject':sub,'set':unquote(u.split('/')[-1]),'session':'Main','medium':'English','source':u,'localPdf':str(out.relative_to(ROOT)),'pages':len(imgs),'status':'downloaded','analysisStatus':'needs OCR','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'notes':'Local PDF assembled from the publicly displayed original page scans.','scanUrls':h.urls}
    except Exception as e:print('ERROR',l['href'],str(e),flush=True)

if __name__=='__main__':
    a=next(r for r in json.loads((ROOT/'sources/archives.json').read_text()) if 'maharashtraboardbooks' in r['url'])
    links=[l for l in a['links'] if re.search(r'/English/(?:200[7-9]|201\d)/Paper-A$',l['href']) or re.search(r'/Computer',l['href'])]
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for r in pool.map(get_paper,links):
            if r:rows.append(r);print(r['year'],r['subject'],r['pages'],flush=True)
            (ROOT/'sources/scan-papers.json').write_text(json.dumps(rows,indent=2))
