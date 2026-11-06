"""Assemble unchanged pages exported from a public browser viewer, in page order."""
import json,hashlib,shutil
from pathlib import Path
from PIL import Image
from harvest import ROOT
rows=[]
for item in json.loads((ROOT/'sources/shaalaa-exports.json').read_text()):
 ident=hashlib.sha256(item['source'].encode()).hexdigest()[:12]
 folder=ROOT/'sources/scans'/ident;folder.mkdir(parents=True,exist_ok=True)
 pages=[]
 for i,a in enumerate(item['assets'],1):
  dest=folder/f'{i:02}.jpg';shutil.copyfile(a['path'],dest);pages.append(Image.open(dest).convert('RGB'))
 pdf=ROOT/'sources/papers'/f'{ident}.pdf';pages[0].save(pdf,'PDF',save_all=True,append_images=pages[1:],resolution=150)
 rows.append({'id':ident,'subject':item['subject'],'year':item['year'],'session':'Main','medium':'English','set':'Public scan','status':'downloaded','analysisStatus':'pending','source':item['source'],'localPdf':str(pdf.relative_to(ROOT)),'pages':len(pages),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'imageSources':[a['url'] for a in item['assets']],'notes':'PDF assembled from the complete publicly visible scan pages; page order and content preserved.'})
 print(ident,item['subject'],item['year'],len(pages))
(ROOT/'sources/shaalaa-recoveries.json').write_text(json.dumps(rows,indent=2))
