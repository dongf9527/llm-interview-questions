# -*- coding: utf-8 -*-
"""报告公共模块：字体注册、Crystal Blue 色板、样式系统、辅助 Flowable
遵循 report.md brief + Template 07 Crystal Blue 正文色板
"""
import os
import sys
import hashlib

PDF_SKILL_DIR = '/home/z/my-project/skills/pdf'
_scripts = os.path.join(PDF_SKILL_DIR, 'scripts')
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, KeepTogether, CondPageBreak, HRFlowable, Preformatted)
from reportlab.platypus.tableofcontents import TableOfContents

# ============ 字体注册（仅允许的字体清单） ============
FONT_DIR = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('NotoSerifSC', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
# 注：静态版 NotoSansSC-Regular.ttf 在本机不存在（仅有变量字体，ReportLab 不支持），
# 全文档统一使用 NotoSerifSC 家族，无需注册 Noto Sans SC。
pdfmetrics.registerFont(TTFont('SarasaMonoSC', f'{FONT_DIR}/truetype/chinese/SarasaMonoSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif', f'{FONT_DIR}/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Bold', f'{FONT_DIR}/truetype/freefont/FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Italic', f'{FONT_DIR}/truetype/freefont/FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-BoldItalic', f'{FONT_DIR}/truetype/freefont/FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))

registerFontFamily('NotoSerifSC', normal='NotoSerifSC', bold='NotoSerifSC-Bold')
registerFontFamily('FreeSerif', normal='FreeSerif', bold='FreeSerif-Bold',
                   italic='FreeSerif-Italic', boldItalic='FreeSerif-BoldItalic')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans')
registerFontFamily('SarasaMonoSC', normal='SarasaMonoSC', bold='SarasaMonoSC')

# 混排字形回退（必调）
from pdf import install_font_fallback
install_font_fallback()

# ---- CJK 禁则补丁：ReportLab 4.x 的 ALL_CANNOT_START 缺少全角标点 ----
# 缺「，：；！？—…」导致行首标点违例。单 frag 路径走 textsplit.dumbSplit，
# 多 frag 路径走 paragraph.cjkFragSplit，两处模块属性都要补
import reportlab.lib.textsplit as _rl_ts
import reportlab.platypus.paragraph as _rl_para
_KINSOKU_EXTRA = '，：；！？—…％、）】》」』'
if not set(_KINSOKU_EXTRA) <= set(_rl_ts.ALL_CANNOT_START):
    _rl_ts.ALL_CANNOT_START = _rl_ts.ALL_CANNOT_START + _KINSOKU_EXTRA
if not set(_KINSOKU_EXTRA) <= set(_rl_para.ALL_CANNOT_START):
    _rl_para.ALL_CANNOT_START = _rl_para.ALL_CANNOT_START + _KINSOKU_EXTRA

# ============ Template 07 Crystal Blue 正文色板 ============
PAGE_BG      = colors.HexColor('#f5f8fc')   # XL 页面底色
SECTION_BG   = colors.HexColor('#edf2f9')   # XL 区块底
CARD_BG      = colors.HexColor('#e4ecf5')   # L 卡片底
TABLE_STRIPE = colors.HexColor('#eef3fa')   # L 表格条纹
HEADER_FILL  = colors.HexColor('#1a4a7a')   # M 表头/结构填充
BORDER       = colors.HexColor('#c0d0e2')   # S 边线
ACCENT       = colors.HexColor('#2d7ab3')   # XS 强调
TEXT_PRIMARY = colors.HexColor('#142840')   # 正文
TEXT_MUTED   = colors.HexColor('#5a7a96')   # 次要文本

# ============ 版面参数 ============
PAGE_W, PAGE_H = A4
MARGIN = 1.0 * inch                       # 左右对称
TOP_MARGIN = 0.95 * inch
BOTTOM_MARGIN = 0.85 * inch
AVAIL_W = PAGE_W - 2 * MARGIN              # ≈ 451pt
AVAIL_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN
H1_COND = AVAIL_H * 0.25                   # H1 孤行阈值

DOC_TITLE = 'llm-interview-questions 项目评估与实验手册'
DOC_AUTHOR = 'Z.ai'

# ============ 样式系统 ============
S = {}
S['body'] = ParagraphStyle('Body', fontName='NotoSerifSC', fontSize=10.5,
    leading=18, alignment=TA_LEFT, wordWrap='CJK', textColor=TEXT_PRIMARY,
    firstLineIndent=21, spaceBefore=0, spaceAfter=6)
S['body_ni'] = ParagraphStyle('BodyNI', parent=S['body'], firstLineIndent=0)
S['h1'] = ParagraphStyle('H1', fontName='NotoSerifSC-Bold', fontSize=20,
    leading=28, textColor=HEADER_FILL, alignment=TA_LEFT, wordWrap='CJK',
    spaceBefore=6, spaceAfter=4)
S['h2'] = ParagraphStyle('H2', fontName='NotoSerifSC-Bold', fontSize=14,
    leading=21, textColor=HEADER_FILL, alignment=TA_LEFT, wordWrap='CJK',
    spaceBefore=16, spaceAfter=7)
S['h3'] = ParagraphStyle('H3', fontName='NotoSerifSC-Bold', fontSize=11.5,
    leading=17, textColor=TEXT_PRIMARY, alignment=TA_LEFT, wordWrap='CJK',
    spaceBefore=12, spaceAfter=5)
S['bullet'] = ParagraphStyle('Bullet', fontName='NotoSerifSC', fontSize=10.5,
    leading=17.5, alignment=TA_LEFT, wordWrap='CJK', textColor=TEXT_PRIMARY,
    leftIndent=16, firstLineIndent=0, spaceBefore=0, spaceAfter=4,
    bulletIndent=4, bulletFontName='NotoSerifSC')
S['caption'] = ParagraphStyle('Caption', fontName='NotoSerifSC', fontSize=8.5,
    leading=12, alignment=TA_CENTER, textColor=TEXT_MUTED, wordWrap='CJK',
    spaceBefore=0, spaceAfter=0)
S['code'] = ParagraphStyle('Code', fontName='SarasaMonoSC', fontSize=8,
    leading=11.5, textColor=TEXT_PRIMARY, alignment=TA_LEFT)
S['th'] = ParagraphStyle('TH', fontName='NotoSerifSC-Bold', fontSize=9.5,
    leading=13.5, alignment=TA_CENTER, textColor=colors.white, wordWrap='CJK')
S['td'] = ParagraphStyle('TD', fontName='NotoSerifSC', fontSize=9,
    leading=13, alignment=TA_LEFT, wordWrap='CJK', textColor=TEXT_PRIMARY)
S['tdc'] = ParagraphStyle('TDC', parent=S['td'], alignment=TA_CENTER)
S['stat_num'] = ParagraphStyle('StatNum', fontName='FreeSerif-Bold',
    fontSize=19, leading=23, textColor=ACCENT, alignment=TA_CENTER)
S['stat_lbl'] = ParagraphStyle('StatLbl', fontName='NotoSerifSC', fontSize=8.5,
    leading=12, textColor=TEXT_MUTED, alignment=TA_CENTER, wordWrap='CJK')
S['callout'] = ParagraphStyle('Callout', fontName='NotoSerifSC', fontSize=10,
    leading=17, alignment=TA_LEFT, wordWrap='CJK', textColor=TEXT_PRIMARY)
S['callout_t'] = ParagraphStyle('CalloutT', fontName='NotoSerifSC-Bold',
    fontSize=10, leading=15, textColor=HEADER_FILL, wordWrap='CJK')
S['quote'] = ParagraphStyle('Quote', fontName='NotoSerifSC', fontSize=10,
    leading=17, leftIndent=24, textColor=TEXT_MUTED, wordWrap='CJK')
S['toc0'] = ParagraphStyle('TOC0', fontName='NotoSerifSC-Bold', fontSize=11,
    leading=20, textColor=TEXT_PRIMARY, leftIndent=6, wordWrap='CJK')
S['toc1'] = ParagraphStyle('TOC1', fontName='NotoSerifSC', fontSize=9.5,
    leading=16, textColor=TEXT_MUTED, leftIndent=26, wordWrap='CJK')
S['toc_title'] = ParagraphStyle('TOCTitle', fontName='NotoSerifSC-Bold',
    fontSize=18, leading=26, textColor=HEADER_FILL, spaceAfter=14)

# ============ 文档模板（含 TOC 支持） ============
class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            level = getattr(flowable, 'bookmark_level', 0)
            text = getattr(flowable, 'bookmark_text', '')
            key = getattr(flowable, 'bookmark_key', '')
            self.notify('TOCEntry', (level, text, self.page, key))

def _paint_bg(cv, doc):
    """Crystal Blue 浅蓝页面底色 + 页眉页脚（onPage 回调，参数为 canvas+doc）"""
    cv.saveState()
    cv.setFillColor(PAGE_BG)
    cv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # 页眉：文档标题（左）+ 强调色细线
    cv.setFont('NotoSerifSC', 7.5)
    cv.setFillColor(TEXT_MUTED)
    cv.drawString(MARGIN, PAGE_H - 0.62 * inch, DOC_TITLE)
    cv.setStrokeColor(ACCENT)
    cv.setLineWidth(1.2)
    cv.line(MARGIN, PAGE_H - 0.70 * inch, PAGE_W - MARGIN, PAGE_H - 0.70 * inch)
    # 页脚：作者（左）+ 页码（右）+ 浅色线
    cv.setStrokeColor(BORDER)
    cv.setLineWidth(0.5)
    cv.line(MARGIN, 0.62 * inch, PAGE_W - MARGIN, 0.62 * inch)
    cv.setFont('NotoSerifSC', 7.5)
    cv.setFillColor(TEXT_MUTED)
    cv.drawString(MARGIN, 0.44 * inch, DOC_AUTHOR)
    cv.setFont('FreeSerif', 8)
    cv.drawRightString(PAGE_W - MARGIN, 0.44 * inch, str(cv.getPageNumber()))
    cv.restoreState()

def make_doc(path):
    return TocDocTemplate(
        path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN,
        title=DOC_TITLE, author=DOC_AUTHOR, creator='Z.ai',
        subject='GitHub 开源项目 llm-interview-questions 评估报告与一个月实验手册')

# ============ 辅助函数 ============
def add_heading(text, level=0, toc_text=None):
    """带书签的标题。level 0 = H1, 1 = H2, 2 = H3(不进目录)"""
    style = S['h1'] if level == 0 else (S['h2'] if level == 1 else S['h3'])
    key = 'h_' + hashlib.md5(text.encode()).hexdigest()[:8]
    p = Paragraph('<a name="%s"/>%s' % (key, text), style)
    if level <= 1:
        p.bookmark_name = key
        p.bookmark_level = level
        p.bookmark_text = toc_text or text
        p.bookmark_key = key
    return p

def h1_block(text, first_para=None):
    """H1 + 强调色下划线 + 首段，防孤行"""
    items = [add_heading(text, 0),
             HRFlowable(width='100%', thickness=1.1, color=ACCENT,
                        spaceBefore=0, spaceAfter=10)]
    if first_para is not None:
        items.append(first_para)
    return [CondPageBreak(H1_COND), KeepTogether(items)]

def h2_block(text, first_para=None):
    items = [add_heading(text, 1)]
    if first_para is not None:
        items.append(first_para)
    return [KeepTogether(items)]

def h3_block(text, first_para=None):
    items = [add_heading(text, 2)]
    if first_para is not None:
        items.append(first_para)
    return [KeepTogether(items)]

def P(text, style='body'):
    return Paragraph(text, S[style])

def bullets(items):
    out = []
    for it in items:
        out.append(Paragraph(it, S['bullet'], bulletText='•'))
    return out

def code_block(code, label=None):
    """代码块：SarasaMonoSC + 卡片底 + 强调色左边线"""
    lines = []
    if label:
        lines.append(Paragraph(label, S['callout_t']))
    pre = Preformatted(code, S['code'])
    tbl = Table([[pre]], colWidths=[AVAIL_W - 6])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
        ('LINEBEFORE', (0, 0), (0, -1), 2, ACCENT),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    tbl.hAlign = 'CENTER'
    if len(lines) > 60 or len(code.splitlines()) > 38:
        return lines + [tbl]
    return lines + [KeepTogether(tbl)]

def callout_box(title, body_text):
    """提示框：4pt 左强调边线 + 浅蓝底"""
    inner = [[Paragraph(title, S['callout_t'])],
             [Paragraph(body_text, S['callout'])]]
    tbl = Table(inner, colWidths=[AVAIL_W - 10])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
    ]))
    tbl.hAlign = 'CENTER'
    return tbl

def stat_row(stats):
    """关键数字行：[(num, label), ...] 4-5 列"""
    n = len(stats)
    gap = 8
    cw = (AVAIL_W - gap * (n - 1)) / n
    cells, widths = [], []
    for i, (num, lbl) in enumerate(stats):
        box = Table([[Paragraph('<b>%s</b>' % num, S['stat_num'])],
                     [Paragraph(lbl, S['stat_lbl'])]], colWidths=[cw])
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
            ('BOX', (0, 0), (-1, -1), 0.75, BORDER),
            ('TOPPADDING', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
            ('TOPPADDING', (0, 1), (-1, 1), 0),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        cells.append(box)
        widths.append(cw)
        if i < n - 1:
            cells.append('')
            widths.append(gap)
    row = Table([cells], colWidths=widths)
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    row.hAlign = 'CENTER'
    return row

def data_table(headers, rows, ratios=None, align_center_cols=None, fontsize=None):
    """标准数据表：深蓝表头 + 白/浅蓝条纹 + 全 Paragraph 单元格"""
    n = len(headers)
    if ratios is None:
        ratios = [1.0 / n] * n
    total = sum(ratios)
    widths = [r / total * AVAIL_W for r in ratios]
    th, td, tdc = S['th'], S['td'], S['tdc']
    if fontsize:
        th = ParagraphStyle('THx', parent=S['th'], fontSize=fontsize, leading=fontsize + 4)
        td = ParagraphStyle('TDx', parent=S['td'], fontSize=fontsize, leading=fontsize + 4)
        tdc = ParagraphStyle('TDCx', parent=td, alignment=TA_CENTER)
    align_center_cols = align_center_cols or set()
    data = [[Paragraph('<b>%s</b>' % h, th) for h in headers]]
    for r in rows:
        row = []
        for j, c in enumerate(r):
            st = tdc if j in align_center_cols else td
            row.append(Paragraph(str(c), st))
        data.append(row)
    tbl = Table(data, colWidths=widths, repeatRows=1, hAlign='CENTER')
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        style.append(('BACKGROUND', (0, i), (-1, i),
                      TABLE_STRIPE if i % 2 == 0 else colors.white))
    tbl.setStyle(TableStyle(style))
    return tbl

def embed_chart(path, caption_text, max_w=None, max_h=230):
    """图表 + 图注（块级、保持纵横比、防撕裂）"""
    from PIL import Image as PILImage
    if max_w is None:
        max_w = AVAIL_W * 0.92
    im = PILImage.open(path)
    ow, oh = im.size
    ratio = min(max_w / ow, max_h / oh, 1.0)
    img = Image(path, width=ow * ratio, height=oh * ratio)
    img.hAlign = 'CENTER'
    cap = Paragraph(caption_text, S['caption'])
    return [Spacer(1, 14), KeepTogether([img, Spacer(1, 7), cap]), Spacer(1, 14)]

def table_with_caption(tbl, caption_text):
    return [Spacer(1, 12), tbl, Spacer(1, 5),
            Paragraph(caption_text, S['caption']), Spacer(1, 12)]
