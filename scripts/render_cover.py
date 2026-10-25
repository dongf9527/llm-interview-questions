# -*- coding: utf-8 -*-
"""用 Playwright(Chromium) 将 cover.html 渲染为 build/cover.pdf（A4，含背景）

依赖：
    pip install playwright
    playwright install chromium

说明：
    cover.html 引用了 Google Fonts 的 Noto Serif SC / Inter；无外网时
    Chromium 自动回退到系统字体（本机需安装 Noto Serif SC）。
    输出尺寸 794x1123 px，与 HTML 的 @page 一致；后续 merge_pdf.py
    会统一归一化为标准 A4（595.28 x 841.89 pt）。
"""
import os

from playwright.sync_api import sync_playwright

_HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(_HERE, 'cover.html')
OUT = os.path.join(_HERE, '..', 'build', 'cover.pdf')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 794, 'height': 1123})
    page.goto('file://' + os.path.abspath(HTML))
    page.wait_for_timeout(1500)          # 等待网络字体加载（如可用）
    page.pdf(path=OUT, width='794px', height='1123px',
             print_background=True, page_ranges='1')
    browser.close()

print('cover.pdf done ->', os.path.abspath(OUT))
