import re,json,hashlib
from harvest import ROOT,fetch
from collect import download
rows=[]
for roman in ['i','ii']:
 u=f'https://targetpublications.org/download/hsc-science-computer-science-{roman}-question-paper-march-2025'
 h=fetch(u).read_text();url=re.search(r'https://cdn\.targetpublications\.org/admin/downloads/[^\\"<>]+\.pdf',h).group()
 rows.append(download({'id':hashlib.sha256(url.encode()).hexdigest()[:12],'year':2025,'subject':'Computer Science '+roman.upper(),'session':'Main','medium':'English','set':'Main','source':u,'pdfUrl':url}))
(ROOT/'sources/target-recoveries.json').write_text(json.dumps(rows,indent=2))
print([(p['id'],p['status'],p.get('pages')) for p in rows])
