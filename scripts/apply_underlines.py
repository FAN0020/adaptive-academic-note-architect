#!/usr/bin/env python3
"""Apply explicit takeaway spans to DOCX without rewriting content."""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from zipfile import ZipFile
from lxml import etree as ET
from docx_utils import NS, W, parse, paragraphs, visible_text, style_id, content_signature

def ranges_for(text, spans):
    ranges=[]
    for s in spans:
        needle=s['text']
        if not isinstance(needle,str) or not needle: raise ValueError('Empty/non-string selected span')
        starts=[]; start=0
        while True:
            at=text.find(needle,start)
            if at<0:break
            starts.append(at);start=at+1
        occurrence=s.get('occurrence')
        if occurrence is None:
            if len(starts)!=1: raise ValueError(f'Span has {len(starts)} matches; require one exact match or occurrence: {needle!r}')
            occurrence=1
        if not isinstance(occurrence,int) or not 1<=occurrence<=len(starts): raise ValueError('Invalid span occurrence')
        a=starts[occurrence-1];ranges.append((a,a+len(needle)))
    ranges.sort()
    if any(a<prev_b for (_,prev_b),(a,_) in zip(ranges,ranges[1:])): raise ValueError('Selected spans overlap')
    return ranges

def apply(source, selections, output):
    source,output=Path(source),Path(output)
    if source.resolve()==output.resolve():raise ValueError('Output must differ from source')
    with ZipFile(source) as z:
        infos=z.infolist();data={i.filename:z.read(i) for i in infos}
    root=parse(data['word/document.xml']);ps=paragraphs(root)
    styles={}
    if 'word/styles.xml' in data:
        styles={s.get(W+'styleId'):s for s in parse(data['word/styles.xml']).findall('w:style',NS)}
    def protected_style(sid):
        seen=set()
        while sid and sid not in seen:
            seen.add(sid)
            if sid.lower().startswith(('heading','title','toc')):return True
            s=styles.get(sid)
            if s is None:break
            name=s.find('w:name',NS);outline=s.find('w:pPr/w:outlineLvl',NS)
            if name is not None and re.match(r'(heading|title|toc)\b',name.get(W+'val',''),re.I):return True
            if outline is not None and int(outline.get(W+'val','9'))<9:return True
            base=s.find('w:basedOn',NS);sid=base.get(W+'val') if base is not None else None
        return False
    seen=set();count=0
    for selection in selections:
        idx=selection['paragraph_index']
        if not isinstance(idx,int) or not 0<=idx<len(ps) or idx in seen:raise ValueError('Invalid/duplicate paragraph index')
        seen.add(idx);p=ps[idx]
        outline=p.find('w:pPr/w:outlineLvl',NS)
        if protected_style(style_id(p)) or (outline is not None and int(outline.get(W+'val','9'))<9):
            raise ValueError('Do not underline headings or TOC entries')
        if p.findall('.//w:fldChar',NS) or p.findall('.//w:instrText',NS) or p.findall('.//w:fldSimple',NS):
            raise ValueError('Field-containing paragraphs require specialized editing')
        if p.findall('.//w:p',NS):raise ValueError('Nested paragraphs require specialized editing')
        txt=visible_text(p)
        if 'expected_text' in selection and selection['expected_text']!=txt:raise ValueError(f'Stale paragraph {idx}')
        ranges=ranges_for(txt,selection['spans']);processed=0;offset=0
        # Children outside simple text runs count toward offsets but cannot be changed.
        for child in list(p):
            rt=visible_text(child);lo,hi=offset,offset+len(rt);offset=hi
            hits=[(max(a,lo),min(b,hi)) for a,b in ranges if a<hi and b>lo]
            if not hits:continue
            if child.tag!=W+'r' or any(c.tag not in (W+'rPr',W+'t') for c in child):
                raise ValueError(f'Paragraph {idx}: span overlaps a field, hyperlink, math, drawing or other unsupported structure')
            cuts=sorted({0,len(rt)}|{v-lo for a,b in hits for v in (a,b)})
            position=p.index(child)
            for left,right in zip(cuts,cuts[1:]):
                if left==right:continue
                nr=deepcopy(child)
                for t in nr.findall('w:t',NS):nr.remove(t)
                t=ET.SubElement(nr,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=rt[left:right]
                if any(a<=lo+left and lo+right<=b for a,b in ranges):
                    rp=nr.find('w:rPr',NS)
                    if rp is None:rp=ET.Element(W+'rPr');nr.insert(0,rp)
                    for u in rp.findall('w:u',NS):rp.remove(u)
                    u=ET.SubElement(rp,W+'u');u.set(W+'val','single');u.set(W+'color','000000')
                    processed+=right-left
                p.insert(position,nr);position+=1
            p.remove(child)
        if processed!=sum(b-a for a,b in ranges):raise ValueError(f'Paragraph {idx}: incomplete span application')
        if visible_text(p)!=txt:raise ValueError('Text preservation failed')
        count+=len(ranges)
    data['word/document.xml']=ET.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.'+output.name+'.',suffix='.docx',dir=output.parent);os.close(fd)
    try:
        with ZipFile(tmp,'w') as z:
            for info in infos:z.writestr(info,data[info.filename])
        if content_signature(source)!=content_signature(tmp):raise ValueError('Package content/equation preservation failed')
        with ZipFile(tmp) as z:
            if z.testzip():raise ValueError('Invalid output package')
        os.replace(tmp,output)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return {'paragraphs_marked':len(seen),'spans_marked':count,'content_preserved':True,'output':str(output)}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('selections',type=Path);ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args(argv)
    try:
        result=apply(args.input,json.loads(args.selections.read_text(encoding='utf-8')),args.output)
        print(json.dumps(result,ensure_ascii=False));return 0
    except Exception as e:print(str(e),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
