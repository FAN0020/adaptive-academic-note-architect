#!/usr/bin/env python3
"""Structural checks only; semantic and visual QA remain necessary."""
import argparse
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile
from docx_utils import NS,W,parse,read_docx,paragraphs,visible_text,style_id,content_signature,sha256,write_json

def norm(text):return re.sub(r'\s+','',text)

def rendered_line_blocks(text):
    """Preserve line boundaries so the next heading's number is not a page number."""
    lines=text.splitlines()
    for i in range(len(lines)):
        for size in (1,2,3):
            if i+size<=len(lines):yield norm(''.join(lines[i:i+size]))

def rendered_toc_entry(text,title,page):
    pattern=re.escape(norm(title))+r'[.·…．]*'+str(page)
    return any(re.fullmatch(pattern,block) for block in rendered_line_blocks(text))

def toc_policy(pages,complex_structure=False,override='auto'):
    if override=='required':return 'required'
    if override=='off':return 'user_opt_out'
    if pages is None:return 'page_count_unverified'
    if pages>10:return 'required'
    if pages>=6:return 'required_for_complex_structure' if complex_structure else 'optional_simple_structure'
    return 'usually_unnecessary'

def audit_coverage(ledger):
    errors=[];units=ledger.get('units',[])
    if not isinstance(units,list) or not units:return ['Coverage ledger must contain a nonempty units list']
    ids=[u.get('id') for u in units]
    if not all(isinstance(i,str) and i for i in ids) or len(set(ids))!=len(ids):return ['Invalid or duplicate coverage unit IDs']
    lookup={u['id']:u for u in units}
    allowed={'covered','merged_duplicate','uncertain_retained','excluded_noncontent','out_of_scope','missing'}
    for u in units:
        tag=u['id'];status=u.get('status')
        for key in ('source','location','meaning','kind'):
            if not isinstance(u.get(key),str) or not u[key].strip():errors.append(f'{tag}: missing {key}')
        if status not in allowed:errors.append(f'{tag}: invalid status')
        if status=='missing':errors.append(f'{tag}: meaningful source content is unaccounted for')
        if status in {'covered','uncertain_retained'} and not u.get('destination'):errors.append(f'{tag}: missing destination')
        if status in {'uncertain_retained','excluded_noncontent','out_of_scope'} and not u.get('reason'):errors.append(f'{tag}: missing reason')
        if status=='merged_duplicate':
            seen={tag};target=u.get('merged_into')
            while True:
                if target not in lookup:errors.append(f'{tag}: missing merge target');break
                if target in seen:errors.append(f'{tag}: cyclic duplicate references');break
                seen.add(target);v=lookup[target]
                if v.get('status')!='merged_duplicate':
                    if v.get('status') not in {'covered','uncertain_retained'}:errors.append(f'{tag}: duplicate resolves to uncovered content')
                    break
                target=v.get('merged_into')
    return errors

def validate(path,pdf=None,before=None,coverage=None,toc='auto',complex_structure='auto',page_offset=0):
    path=Path(path);errors=[];warnings=[]
    report={'input':str(path.resolve()),'input_sha256':sha256(path),'errors':errors,'warnings':warnings,
            'semantic_coverage':'not_certified','visual_qa':'not_performed_by_script','citation_truth':'not_certified'}
    if path.suffix.lower() in {'.md','.markdown'}:
        text=path.read_text(encoding='utf-8')
        report['headings']=len(re.findall(r'^#{1,6}\s+',text,re.M))
        report['underline_markup_spans']=len(re.findall(r'<u\b',text,re.I))
        if text.lower().count('<u>')!=text.lower().count('</u>'):errors.append('Unbalanced underline tags')
        warnings.append('Markdown is unpaginated; HTML underline support and anchor navigation require renderer review')
        if before and path.read_text()!=Path(before).read_text():errors.append('Exact Markdown text differs; inspect permitted markup-only changes separately')
        pages=None
    elif path.suffix.lower()=='.docx':
        root=read_docx(path);ps=paragraphs(root)
        with ZipFile(path) as z:
            styles=parse(z.read('word/styles.xml')) if 'word/styles.xml' in z.namelist() else None
        levels={}
        if styles is not None:
            for s in styles.findall('w:style',NS):
                sid=s.get(W+'styleId');name=s.find('w:name',NS);outline=s.find('w:pPr/w:outlineLvl',NS)
                m=re.search(r'heading\s*([1-9])',name.get(W+'val','') if name is not None else '',re.I)
                if m:levels[sid]=int(m.group(1))
                elif outline is not None and int(outline.get(W+'val','9'))<9:levels[sid]=int(outline.get(W+'val'))+1
        headings=[(p,levels.get(style_id(p))) for p in ps if style_id(p) in levels]
        report['headings']=len(headings)
        report['paragraphs']=len(ps)
        marked=[]
        for i,p in enumerate(ps):
            texts=[]
            for r in p.findall('.//w:r',NS):
                u=r.find('w:rPr/w:u',NS)
                if u is not None and u.get(W+'val','single') not in ('none','0','false'):texts.append(visible_text(r))
            if texts:marked.append({'paragraph_index':i,'text':''.join(texts)})
        report['paragraphs_with_direct_underlines']=len(marked)
        if not marked:warnings.append('No direct underlined takeaways found; check inherited styling or add semantic selections')
        anchors={b.get(W+'name'):b for b in root.findall('.//w:bookmarkStart',NS)}
        links=root.findall('.//w:hyperlink',NS)
        for h in links:
            anchor=h.get(W+'anchor')
            if anchor and anchor not in anchors:errors.append('Broken internal anchor: '+anchor)
        entries=[]
        for h in links:
            anchor=h.get(W+'anchor');t=visible_text(h)
            m=re.fullmatch(r'(.+?)\t+\s*(\d+)\s*',t,re.S)
            if not (anchor and m):continue
            title=m.group(1).strip();number=int(m.group(2))
            entries.append({'title':title,'page':number,'anchor':anchor})
            if anchor in anchors:
                p=anchors[anchor]
                while p is not None and p.tag!=W+'p':p=p.getparent()
                if p is None or norm(title)!=norm(visible_text(p)):errors.append('TOC title differs from bookmark heading: '+title)
        report['toc_entries']=len(entries)
        inferred_complex=sum(level==1 for _,level in headings)>=4 or sum(level in (1,2) for _,level in headings)>=10
        complex_value=inferred_complex if complex_structure=='auto' else complex_structure=='yes'
        report['complex_structure']=complex_value
        pages=None
        if pdf:
            from pypdf import PdfReader
            pdf=Path(pdf);r=PdfReader(pdf);pages=len(r.pages)
            report['rendered_pdf_sha256']=sha256(pdf)
            page_texts=[p.extract_text() or '' for p in r.pages]
            if pdf.stat().st_mtime<path.stat().st_mtime:warnings.append('PDF predates DOCX; confirm final render provenance before delivery')
            verified=0
            for entry in entries:
                physical=entry['page']-page_offset
                if not 1<=physical<=pages:
                    errors.append('TOC page out of range: '+entry['title']);continue
                title=norm(entry['title'])
                if title not in set(rendered_line_blocks(page_texts[physical-1])):
                    errors.append('Heading not found on cited body page: '+entry['title']);continue
                verified+=1
            report['toc_heading_pages_verified']=verified
            # Verify link destinations grouped by contents page and visual y position.
            from collections import defaultdict
            on_pages=defaultdict(list)
            for entry in entries:
                matches=[i for i,t in enumerate(page_texts) if rendered_toc_entry(t,entry['title'],entry['page'])]
                if len(matches)==1:on_pages[matches[0]].append(entry)
                else:warnings.append('Cannot uniquely locate rendered TOC entry: '+entry['title'])
            link_verified=0
            for i,items in on_pages.items():
                anns=[]
                for ref in r.pages[i].get('/Annots',[]):
                    a=ref.get_object();dest=a.get('/Dest')
                    action=a.get('/A')
                    if dest is None and action is not None:dest=action.get_object().get('/D')
                    if isinstance(dest,list) and dest and a.get('/Rect') is not None:anns.append((a,dest))
                anns.sort(key=lambda ad:float(ad[0]['/Rect'][3]),reverse=True)
                if len(anns)!=len(items):
                    warnings.append(f'PDF page {i+1}: link annotation layout needs manual verification');continue
                for entry,(_,dest) in zip(items,anns):
                    actual=next((k+1 for k,p in enumerate(r.pages) if p.indirect_reference==dest[0]),None)
                    if actual!=entry['page']-page_offset:errors.append('TOC PDF link destination mismatch: '+entry['title'])
                    else:link_verified+=1
            report['toc_pdf_link_destinations_verified']=link_verified
        else:warnings.append('No rendered PDF: page count, TOC numbers, glyphs and pagination are unverified')
        policy=toc_policy(pages,complex_value,toc);report['toc_policy']=policy
        if policy in ('required','required_for_complex_structure') and not entries:errors.append('Page-numbered linked TOC required but no supported entries found')
        if before:
            same=content_signature(path)==content_signature(before)
            report['exact_content_preserved']=same
            if not same:errors.append('Paragraph text or native equation content changed during format-only comparison')
    else:raise ValueError('Supported outputs are DOCX and Markdown; render/inspect PDF outputs with the PDF workflow')
    report['rendered_pages']=pages
    if coverage:
        ledger=json.loads(Path(coverage).read_text(encoding='utf-8'))
        coverage_errors=audit_coverage(ledger);errors.extend(coverage_errors)
        report['coverage_ledger_consistent']=not coverage_errors
        report['coverage_units']=len(ledger.get('units',[]))
    report['structural_checks_passed']=not errors
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--rendered-pdf',type=Path);ap.add_argument('--before',type=Path)
    ap.add_argument('--coverage',type=Path);ap.add_argument('--report',type=Path)
    ap.add_argument('--toc',choices=['auto','required','off'],default='auto')
    ap.add_argument('--complex-structure',choices=['auto','yes','no'],default='auto')
    ap.add_argument('--page-offset',type=int,default=0)
    args=ap.parse_args(argv)
    try:
        report=validate(args.input,args.rendered_pdf,args.before,args.coverage,args.toc,args.complex_structure,args.page_offset)
        if args.report:
            inputs=[p.resolve() for p in [args.input,args.rendered_pdf,args.before,args.coverage] if p]
            if args.report.resolve() in inputs:raise ValueError('Report must not overwrite an input')
            write_json(args.report,report)
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['structural_checks_passed'] else 1
    except Exception as e:print(str(e),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
