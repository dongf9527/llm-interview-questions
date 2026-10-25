# -*- coding: utf-8 -*-
"""主脚本：组装 9 章 story，multiBuild 生成正文 PDF（封面另行合并）"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from report_common import (
    S, make_doc, _paint_bg, DOC_TITLE, Spacer, Paragraph, PageBreak,
    TableOfContents)
from reportlab.platypus.tableofcontents import TableOfContents
import report_content_a as A
import report_content_b as B

_BUILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build')
os.makedirs(_BUILD, exist_ok=True)
OUT = os.path.join(_BUILD, 'body.pdf')

doc = make_doc(OUT)
story = []

# ---- 目录页（正文 PDF 第 1 页） ----
story.append(Paragraph('目 录', S['toc_title']))
toc = TableOfContents()
toc.levelStyles = [S['toc0'], S['toc1']]
toc.dotsMinLevel = 0
story.append(toc)
story.append(PageBreak())

# ---- 正文九章 ----
A.chapter1(story)
A.chapter2(story)
A.chapter3(story)
A.chapter4(story)
B.chapter5(story)
B.chapter6(story)
B.chapter7(story)
B.chapter8(story)
B.chapter9(story)

doc.multiBuild(story, onFirstPage=_paint_bg, onLaterPages=_paint_bg)
print('body.pdf built, pages =', doc.page)
