#!/usr/bin/env python3
"""Regression checks for preservation, rejection paths, extraction and navigation gates."""
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from lxml import etree as E
from pypdf import PdfWriter
from docx_utils import NS,W,M,parse,paragraphs,visible_text,content_signature
from apply_underlines import apply
from extract_sources import extract,main as extract_main
from validate_output import validate,audit_coverage

def fixture(path,body='<w:p><w:r><w:t>前提。核心</w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>结论。尾声。</w:t></w:r></w:p>'):
    xml=f'<w:document xmlns:w="{NS["w"]}" xmlns:m="{NS["m"]}"><w:body>{body}<w:sectPr/></w:body></w:document>'
    with ZipFile(path,'w') as z:
        z.writestr('word/document.xml',xml)
        z.writestr('word/styles.xml',f'<w:styles xmlns:w="{NS["w"]}"><w:style w:styleId="Heading1"><w:name w:val="heading 1"/></w:style></w:styles>')
        z.writestr('word/fonts/example.odttf',b'unchanged fixture font bytes')
        z.writestr('word/_rels/document.xml.rels',b'unchanged relationships')
    return path

def pdf_fixture(path,n):
    w=PdfWriter()
    for _ in range(n):w.add_blank_page(width=595,height=842)
    w.write(path);return path

class Helpers(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.src=fixture(self.root/'source.docx');self.out=self.root/'result.docx'
    def tearDown(self):self.temp.cleanup()
    def selection(self,text='核心结论。',**extra):
        return [{'paragraph_index':0,'expected_text':'前提。核心结论。尾声。','spans':[{'text':text,**extra}]}]
    def test_cross_run_preserves_text_equations_and_package(self):
        apply(self.src,self.selection(),self.out)
        self.assertEqual(content_signature(self.src),content_signature(self.out))
        with ZipFile(self.src) as a,ZipFile(self.out) as b:
            for k in a.namelist():
                if k!='word/document.xml':self.assertEqual(a.read(k),b.read(k))
            p=paragraphs(parse(b.read('word/document.xml')))[0]
            marked=[r for r in p.findall('w:r',NS) if r.find('w:rPr/w:u',NS) is not None]
            self.assertEqual(''.join(visible_text(r) for r in marked),'核心结论。')
            self.assertIsNotNone(marked[-1].find('w:rPr/w:b',NS))
    def test_equation_is_preserved(self):
        body='<w:p><w:r><w:t>结论。</w:t></w:r></w:p><w:p><m:oMath><m:r><m:t>x²</m:t></m:r></m:oMath></w:p>'
        fixture(self.src,body)
        apply(self.src,[{'paragraph_index':0,'spans':[{'text':'结论。'}]}],self.out)
        self.assertEqual(content_signature(self.src),content_signature(self.out))
    def test_ambiguous_text_is_not_guessed(self):
        with self.assertRaises(ValueError):apply(self.src,self.selection('。'),self.out)
        self.assertFalse(self.out.exists())
    def test_occurrence_is_explicit(self):
        apply(self.src,self.selection('。',occurrence=2),self.out)
        self.assertEqual(content_signature(self.src),content_signature(self.out))
    def test_stale_index_text_rejected(self):
        s=self.selection();s[0]['expected_text']='old text'
        with self.assertRaises(ValueError):apply(self.src,s,self.out)
        self.assertFalse(self.out.exists())
    def test_source_overwrite_rejected(self):
        before=self.src.read_bytes()
        with self.assertRaises(ValueError):apply(self.src,self.selection(),self.src)
        self.assertEqual(self.src.read_bytes(),before)
    def test_unsupported_hyperlink_fails_atomically(self):
        fixture(self.src,'<w:p><w:hyperlink w:anchor="a"><w:r><w:t>结论</w:t></w:r></w:hyperlink></w:p>')
        with self.assertRaises(ValueError):apply(self.src,[{'paragraph_index':0,'spans':[{'text':'结论'}]}],self.out)
        self.assertFalse(self.out.exists())
    def test_equation_overlap_rejected(self):
        fixture(self.src,'<w:p><m:oMath><m:r><m:t>x</m:t></m:r></m:oMath></w:p>')
        with self.assertRaises(ValueError):apply(self.src,[{'paragraph_index':0,'spans':[{'text':'x'}]}],self.out)
    def test_field_result_is_not_modified(self):
        fixture(self.src,'<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>12</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
        with self.assertRaises(ValueError):apply(self.src,[{'paragraph_index':0,'spans':[{'text':'12'}]}],self.out)
        self.assertFalse(self.out.exists())
    def test_inherited_heading_style_is_protected(self):
        fixture(self.src,'<w:p><w:pPr><w:pStyle w:val="Lesson"/></w:pPr><w:r><w:t>Topic</w:t></w:r></w:p>')
        with ZipFile(self.src) as z:data={n:z.read(n) for n in z.namelist()}
        styles=parse(data['word/styles.xml']);s=E.SubElement(styles,W+'style');s.set(W+'styleId','Lesson');b=E.SubElement(s,W+'basedOn');b.set(W+'val','Heading1')
        data['word/styles.xml']=E.tostring(styles)
        with ZipFile(self.src,'w') as z:
            for k,v in data.items():z.writestr(k,v)
        with self.assertRaises(ValueError):apply(self.src,[{'paragraph_index':0,'spans':[{'text':'Topic'}]}],self.out)
        self.assertFalse(self.out.exists())
    def test_extraction_keeps_table_order_and_notes(self):
        fixture(self.src,'<w:p><w:r><w:t>before</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>cell</w:t></w:r></w:p></w:tc></w:tr></w:tbl><w:p><w:r><w:t>after</w:t></w:r></w:p>')
        self.assertEqual([u['text'] for u in extract(self.src)['units']],['before','cell','after'])
    def test_cache_invalidation_and_missing_source(self):
        txt=self.root/'notes.md';manifest=self.root/'sources.json';txt.write_text('first')
        args=[str(txt),'--output',str(manifest),'--reuse']
        self.assertEqual(extract_main(args),0);self.assertEqual(extract_main(args),0)
        self.assertTrue(json.loads(manifest.read_text())['sources'][0]['cache_reused'])
        txt.write_text('second');self.assertEqual(extract_main(args),0)
        self.assertFalse(json.loads(manifest.read_text())['sources'][0]['cache_reused'])
        txt.unlink();self.assertEqual(extract_main(args),2)
        self.assertEqual(len(json.loads(manifest.read_text())['errors']),1)
    def test_eleven_pages_requires_toc(self):
        r=validate(self.src,pdf_fixture(self.root/'x.pdf',11))
        self.assertFalse(r['structural_checks_passed']);self.assertEqual(r['toc_policy'],'required')
    def test_ten_pages_is_conditional(self):
        pdf=pdf_fixture(self.root/'x.pdf',10)
        self.assertTrue(validate(self.src,pdf,complex_structure='no')['structural_checks_passed'])
        self.assertFalse(validate(self.src,pdf,complex_structure='yes')['structural_checks_passed'])
    def test_six_pages_complex_and_five_pages_simple(self):
        self.assertFalse(validate(self.src,pdf_fixture(self.root/'six.pdf',6),complex_structure='yes')['structural_checks_passed'])
        self.assertTrue(validate(self.src,pdf_fixture(self.root/'five.pdf',5))['structural_checks_passed'])
    def test_explicit_toc_override(self):
        self.assertTrue(validate(self.src,pdf_fixture(self.root/'x.pdf',11),toc='off')['structural_checks_passed'])
        self.assertFalse(validate(self.src,pdf_fixture(self.root/'y.pdf',2),toc='required')['structural_checks_passed'])
    def test_no_render_is_not_page_verification(self):
        r=validate(self.src);self.assertIsNone(r['rendered_pages']);self.assertEqual(r['toc_policy'],'page_count_unverified')
    def test_toc_leaders_and_following_numeric_heading(self):
        from reportlab.pdfgen import canvas
        fixture(self.src,'<w:p><w:r><w:t>Contents</w:t></w:r></w:p><w:p><w:hyperlink w:anchor="overview"><w:r><w:t>1 Overview</w:t><w:tab/><w:t>2</w:t></w:r></w:hyperlink></w:p><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:bookmarkStart w:id="1" w:name="overview"/><w:r><w:t>1 Overview</w:t></w:r><w:bookmarkEnd w:id="1"/></w:p>')
        pdf=self.root/'linked.pdf';c=canvas.Canvas(str(pdf))
        c.drawString(50,750,'Contents');c.drawString(50,700,'1 Overview.......................2')
        c.linkRect('', 'overview', (50,696,300,714), relative=0)
        c.showPage();c.bookmarkPage('overview');c.drawString(50,750,'1 Overview');c.drawString(50,720,'1.1 Next heading');c.save()
        r=validate(self.src,pdf,toc='required')
        self.assertTrue(r['structural_checks_passed'],r['errors'])
        self.assertEqual(r['toc_heading_pages_verified'],1)
        self.assertEqual(r['toc_pdf_link_destinations_verified'],1)
    def test_changed_formula_or_text_fails_format_audit(self):
        fixture(self.out,'<w:p><w:r><w:t>different</w:t></w:r></w:p>')
        self.assertFalse(validate(self.out,before=self.src)['exact_content_preserved'])
    def test_coverage_missing_and_cycles_rejected(self):
        unit={'id':'a','source':'x','location':'p1','kind':'knowledge','meaning':'claim','status':'missing'}
        self.assertTrue(audit_coverage({'units':[unit]}))
        a=dict(unit,status='merged_duplicate',merged_into='b');b=dict(a,id='b',merged_into='a')
        self.assertTrue(audit_coverage({'units':[a,b]}))
        a=dict(unit,status='covered',destination='section');b=dict(unit,id='b',status='merged_duplicate',merged_into='a')
        self.assertEqual(audit_coverage({'units':[a,b]}),[])

if __name__=='__main__':unittest.main()
