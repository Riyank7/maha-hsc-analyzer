"""Package only public app assets and active PDFs for static hosting."""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir()
for name in ['index.html','styles.css','app.js','stats.js','404.html','_headers','_redirects']:
 p=ROOT/name
 if p.exists():shutil.copy2(p,OUT/name)
for name in ['data','reports']:
 shutil.copytree(ROOT/name,OUT/name)
papers=json.loads((ROOT/'data/papers.json').read_text())
active=[p for p in papers if p.get('localPdf') and not p.get('duplicateOf') and not p.get('excluded')]
for p in active:
 dest=OUT/p['localPdf'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p['localPdf'],dest)
print(f'Packaged {len(active)} unique PDFs and public app assets into dist/')
