# -*- coding: utf-8 -*-
"""生成评估报告所需图表：模块题量分布横向条形图 + 来源等级环形图
遵循 charts.md 规范：无顶右脊线、值已标注则删网格、环形图中心留指标、图例无边框
"""
import matplotlib
import matplotlib.font_manager as fm
import os

# 中文字体：NotoSansSC 为变量字体，加载失败则回退 wqy-zenhei
_cn_candidates = [
    '/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf',
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
]
_cn_font_name = None
for _p in _cn_candidates:
    if os.path.exists(_p):
        try:
            fm.fontManager.addfont(_p)
            _cn_font_name = fm.FontProperties(fname=_p).get_name()
            break
        except Exception:
            continue
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')

import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = [_cn_font_name or 'sans-serif', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
print(f'chart font: {_cn_font_name}')

# Template 07 Crystal Blue 正文色板（单色系）
ACCENT = '#2d7ab3'
DEEP = '#1a4a7a'
BORDER = '#c0d0e2'
MUTED = '#5a7a96'
TEXT = '#142840'

OUT = '/home/z/my-project/download/assets'

import os
os.makedirs(OUT, exist_ok=True)

# ============ 图1：模块题量分布（横向条形图） ============
modules = [
    ('模型架构', 20), ('模型训练', 11), ('向量检索', 9), ('RLHF与对齐', 8),
    ('Agent', 8), ('多模态', 8), ('评估与监控', 8), ('推理优化', 7),
    ('RAG基础', 6), ('重排与优化', 5), ('模型微调', 4), ('Prompt工程', 3),
    ('知识图谱', 2), ('文档处理', 1),
]
modules_sorted = sorted(modules, key=lambda x: x[1])  # 升序，最大在顶部
names = [m[0] for m in modules_sorted]
counts = [m[1] for m in modules_sorted]

fig, ax = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
# 同色系不同明度：题量越大颜色越深
max_c = max(counts)
colors = [matplotlib.colors.to_hex(
    matplotlib.colors.to_rgba(ACCENT, 0.45 + 0.55 * (c / max_c))) for c in counts]

bars = ax.barh(names, counts, color=colors, edgecolor='none', height=0.62)
# 值标注在条形右端
for bar, c in zip(bars, counts):
    ax.text(bar.get_width() + 0.35, bar.get_y() + bar.get_height() / 2,
            f'{c}', va='center', ha='left', fontsize=10.5, color=TEXT)

# 值已直接标注 → 删除网格；删除顶/右/左脊线
for s in ['top', 'right', 'left']:
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color('#b8c6d4')
ax.spines['bottom'].set_linewidth(0.8)
ax.tick_params(axis='y', length=0, labelsize=10.5, colors=TEXT)
ax.tick_params(axis='x', length=0, labelbottom=False)
ax.set_xlim(0, 22.5)
fig.savefig(f'{OUT}/chart_modules.png', dpi=200, facecolor='white')
plt.close(fig)
print('chart_modules.png done')

# ============ 图2：来源等级环形图（Strategy C：图上零文字+富图例） ============
fig, ax = plt.subplots(figsize=(6.8, 3.6), constrained_layout=True)
tier_vals = [74, 26]
tier_colors = [DEEP, BORDER]
wedges, _ = ax.pie(
    tier_vals, colors=tier_colors, startangle=90, counterclock=False,
    wedgeprops=dict(width=0.35, edgecolor='white', linewidth=2))
# 中心核心指标
ax.text(0, 0.08, '100', ha='center', va='center', fontsize=30,
        color=TEXT, fontweight='bold')
ax.text(0, -0.26, '题', ha='center', va='center', fontsize=12, color=MUTED)
ax.set(aspect='equal')

# 富图例（右侧网格布局，替代图上标注）
legend = ax.legend(
    wedges,
    ['B 级：附可回查资料  74 题（74%）', 'C 级：教学整理  26 题（26%）'],
    loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False,
    fontsize=11, labelspacing=1.2, handlelength=1.0, handleheight=1.0)
for t in legend.get_texts():
    t.set_color(TEXT)
fig.savefig(f'{OUT}/chart_tiers.png', dpi=200, facecolor='white')
plt.close(fig)
print('chart_tiers.png done')
