import concurrent.futures,hashlib,json,re
from harvest import ROOT,fetch,inspect
from collect import download
from urllib.parse import urljoin

rows=[]
res=inspect('https://www.respaper.com/vrajparesh/')
(ROOT/'sources/respaper-index.json').write_text(json.dumps(res,indent=2))
for l in res['links']:
    if 'Computer Science' not in l['text'] or 'March' not in l['text']:continue
    year=re.search(r'20\d\d-(20\d\d)',l['text'])
    if not year:continue
    try:
        p=fetch(l['href']);s=p.read_text(errors='replace');m=re.search(r"var file_name\s*=\s*'([^']+)'",s)
        if not m:continue
        url=urljoin(l['href'],m[1]);ident=hashlib.sha256(url.encode()).hexdigest()[:12]
        sub='Computer Science II' if 'Science 2' in l['text'] else 'Computer Science I'
        rows.append({'id':ident,'subject':sub,'year':int(year[1]),'set':'Paper II' if sub.endswith('II') else 'Paper I','session':'Main','medium':'English','source':l['href'],'pdfUrl':url,'analysisStatus':'pending'})
    except Exception as e:print('ERROR',l,str(e),flush=True)

for year,sub,u in [(2024,'Computer Science I','https://docs.aglasem.com/view/24bd6962-0b83-11ef-a131-0a5e36bc6706'),(2023,'Computer Science I','https://docs.aglasem.com/view/33e4adc6-c5b9-11ed-b0e8-0a5e36bc6706')]:
    p=fetch(u);urls=re.findall(r'https://[^"\s]+\.pdf',p.read_text())
    if urls:
        url=urls[0];rows.append({'id':hashlib.sha256(url.encode()).hexdigest()[:12],'subject':sub,'year':year,'set':'Paper I','session':'Main','medium':'English','source':u,'pdfUrl':url,'analysisStatus':'pending'})
out=[]
with concurrent.futures.ThreadPoolExecutor(4) as pool:
    for row in pool.map(download,rows):
        out.append(row);print(row['year'],row['subject'],row['status'],row.get('pages'),row.get('error'),flush=True)
        (ROOT/'sources/more-papers.json').write_text(json.dumps(out,indent=2))
