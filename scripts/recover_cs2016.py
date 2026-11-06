import json,hashlib
from harvest import ROOT
from collect import download
rows=[]
for n,roman in [(1,'I'),(2,'II')]:
 u=f'https://vocationalacademy.co.in/uploads/hsc-computer-science-question-paper-{n}-march-2016.pdf'
 rows.append(download({'id':hashlib.sha256(u.encode()).hexdigest()[:12],'subject':'Computer Science '+roman,'year':2016,'session':'Main','medium':'English','set':'Paper '+roman,'source':'https://vocationalacademy.co.in/board-papers/','pdfUrl':u}))
(ROOT/'sources/cs2016-recoveries.json').write_text(json.dumps(rows,indent=2));print([(p['id'],p['status'],p.get('pages')) for p in rows])
