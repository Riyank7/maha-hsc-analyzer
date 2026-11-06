"""Package only public app assets and active PDFs for static hosting."""
import json,shutil,subprocess,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir()
for name in ['index.html','styles.css','app.js','stats.js','404.html','_headers','_redirects','_routes.json','login.html','auth.css','login.js','auth-ui.js','privacy.html']:
 p=ROOT/name
 if p.exists():shutil.copy2(p,OUT/name)
for name in ['data','reports']:
 shutil.copytree(ROOT/name,OUT/name)
papers=json.loads((ROOT/'data/papers.json').read_text())
active=[p for p in papers if p.get('localPdf') and not p.get('duplicateOf') and not p.get('excluded')]
for p in active:
 dest=OUT/p['localPdf'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p['localPdf'],dest)
try:
 version=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
except (OSError,subprocess.CalledProcessError):
 version='local'
commit=version
version=commit+':'+(os.environ.get('GITHUB_RUN_ID') or datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f'))
(OUT/'version.json').write_text(json.dumps({'version':version,'commit':commit}))
for name in ['index.html','login.html']:
 p=OUT/name
 if p.exists():p.write_text(p.read_text().replace('</head>',f'<meta name="app-version" content="{version}"></head>'))
print(f'Packaged {len(active)} unique PDFs and public app assets into dist/')
