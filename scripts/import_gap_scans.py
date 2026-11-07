"""Import ordered, unchanged scan images exported from a public viewer."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
manifest = Path(sys.argv[1])
rows = []
for item in json.loads(manifest.read_text()):
    ident = hashlib.sha256(item['source'].encode()).hexdigest()[:12]
    folder = ROOT / 'sources/scans' / ident
    folder.mkdir(parents=True, exist_ok=True)
    images = []
    for i, asset in enumerate(item['assets'], 1):
        destination = folder / f'{i:02}.jpg'
        shutil.copyfile(asset['path'], destination)
        image = Image.open(destination).convert('RGB')
        if image.width < 700:
            raise ValueError(f'Thumbnail instead of full page: {destination}')
        images.append(image)
    pdf = ROOT / 'sources/papers' / f'{ident}.pdf'
    images[0].save(pdf, 'PDF', save_all=True, append_images=images[1:], resolution=150)
    assert len(PdfReader(pdf).pages) == len(images)
    rows.append({
        'id': ident, 'subject': item['subject'], 'year': item['year'],
        'part': item['part'], 'session': 'Main', 'medium': 'English',
        'set': f"Paper {item['part']} · public scan", 'status': 'downloaded',
        'analysisStatus': 'pending', 'source': item['source'],
        'localPdf': str(pdf.relative_to(ROOT)), 'pages': len(images),
        'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
        'imageSources': [a['url'] for a in item['assets']],
        'notes': 'Complete publicly visible scan, assembled in page order. Main exam attribution follows the source archive.',
    })
    print(ident, item['year'], item['subject'], item['part'], len(images))
(ROOT / 'sources/gap-recoveries.json').write_text(json.dumps(rows, indent=2))
