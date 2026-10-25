# -*- coding: utf-8 -*-
"""合并封面 + 正文为单一 PDF，统一 A4 尺寸并写入元数据"""
import os
from pypdf import PdfReader, PdfWriter

A4_W, A4_H = 595.28, 841.89

_BUILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build')
os.makedirs(_BUILD, exist_ok=True)

COVER = os.path.join(_BUILD, 'cover.pdf')
BODY = os.path.join(_BUILD, 'body.pdf')
OUT = os.path.join(_BUILD, 'llm-interview-questions-项目评估与实验手册.pdf')


def normalize(page):
    w, h = float(page.mediabox.width), float(page.mediabox.height)
    if abs(w - A4_W) > 0.1 or abs(h - A4_H) > 0.1:
        page.scale_to(A4_W, A4_H)
        page.mediabox.lower_left = (0, 0)
        page.mediabox.upper_right = (A4_W, A4_H)
    return page


writer = PdfWriter()
writer.add_page(normalize(PdfReader(COVER).pages[0]))
for p in PdfReader(BODY).pages:
    writer.add_page(normalize(p))

writer.add_metadata({
    '/Title': 'llm-interview-questions 项目评估与实验手册',
    '/Author': 'Z.ai',
    '/Creator': 'Z.ai',
    '/Subject': 'GitHub 开源项目 llm-interview-questions 评估报告与一个月实验手册',
})
with open(OUT, 'wb') as f:
    writer.write(f)

r = PdfReader(OUT)
print('merged pages:', len(r.pages))
for i in [0, 1, 2]:
    b = r.pages[i].mediabox
    print(f'page{i}: {float(b.width):.1f} x {float(b.height):.1f}')
