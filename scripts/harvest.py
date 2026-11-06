"""Download public source pages and expose their actual linked files."""
import concurrent.futures, hashlib, json, re, time, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.current=None; self.text=[]; self.scripts=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.current=a.get('href'); self.text=[]
        if tag in ('iframe','embed') and a.get('src'): self.links.append({'href':a['src'],'text':'embedded document'})
        if tag=='script' and a.get('src'): self.scripts.append(a['src'])
    def handle_data(self,data):
        if self.current: self.text.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.current:
            self.links.append({'href':self.current,'text':' '.join(' '.join(self.text).split())}); self.current=None

def fetch(url, folder='pages', suffix='.html'):
    p=ROOT/'sources'/folder/(hashlib.sha256(url.encode()).hexdigest()[:16]+suffix)
    if p.exists(): return p
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; HSCResearch/1.0)'})
    with urllib.request.urlopen(req,timeout=35) as r: data=r.read()
    p.write_bytes(data); return p

def inspect(url):
    p=fetch(url); h=Links(); h.feed(p.read_text(errors='replace'))
    return {'url':url,'path':str(p.relative_to(ROOT)), 'links':[{**l,'href':urljoin(url,l['href'])} for l in h.links], 'scripts':[urljoin(url,s) for s in h.scripts]}

if __name__=='__main__':
    urls=['https://www.isquareit.edu.in/pcm-last-five-years-question-papers/','https://hscexam.vercel.app/','https://www.omtexclasses.com/p/maharashtra-hsc-12th-board-previous.html','https://maharashtraboardbooks.com/papers/HSC']
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(inspect,urls):
            rows.append(row)
            print(row['url'],len(row['links']), 'scripts',row['scripts'])
            for l in row['links']:
                if re.search(r'physics|chemistry|math|english|computer|\.pdf',l['text']+' '+l['href'],re.I): print(json.dumps(l))
    (ROOT/'sources'/'archives.json').write_text(json.dumps(rows,indent=2))
