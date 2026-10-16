"""Small OOXML utilities; no application installation or network access."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as ET
import hashlib
import json
import os
import tempfile

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W, M = '{'+NS['w']+'}', '{'+NS['m']+'}'

def parse(data):
    return ET.fromstring(data, ET.XMLParser(resolve_entities=False, no_network=True))

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def visible_text(node):
    pieces = []
    for e in node.iter():
        if e.tag in (W+'t', M+'t'): pieces.append(e.text or '')
        elif e.tag == W+'tab': pieces.append('\t')
        elif e.tag in (W+'br', W+'cr'): pieces.append('\n')
    return ''.join(pieces)

def read_docx(path):
    with ZipFile(path) as z:
        bad = z.testzip()
        if bad: raise ValueError('Corrupt DOCX part: '+bad)
        return parse(z.read('word/document.xml'))

def paragraphs(root):
    return root.findall('.//w:p', NS)

def style_id(p):
    s = p.find('w:pPr/w:pStyle', NS)
    return s.get(W+'val', '') if s is not None else ''

def content_signature(path):
    """Exact paragraph text and equation trees across text-bearing parts."""
    result = {}
    with ZipFile(path) as z:
        for name in sorted(z.namelist()):
            if not name.startswith('word/') or not name.endswith('.xml'): continue
            root = parse(z.read(name))
            ps = paragraphs(root)
            if not ps: continue
            result[name] = {
                'paragraphs': [visible_text(p) for p in ps],
                'equations': [ET.tostring(m, method='c14n') for m in root.findall('.//m:oMath', NS)]
            }
    return result

def write_json(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.'+target.name+'.', dir=target.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
