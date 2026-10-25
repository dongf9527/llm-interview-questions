# -*- coding: utf-8 -*-
"""内容模块 B：第五至九章（四周实验手册 + 风险建议）"""
from report_common import (
    S, P, add_heading, h1_block, h2_block, h3_block, bullets, code_block,
    callout_box, data_table, table_with_caption, Spacer, Paragraph,
    KeepTogether, AVAIL_W)


def _exp_header(story, no, title, verify, cost):
    """实验信息头：统一的目标/验证题目/耗时表格"""
    story.append(Spacer(1, 4))
    story.append(data_table(
        ['验证题目', '实验耗时', '难度'],
        [[verify, cost, _DIFF.get(no, '中等')]],
        ratios=[0.56, 0.24, 0.20], align_center_cols={1, 2}, fontsize=8.5))
    story.append(Spacer(1, 8))


_DIFF = {}


def chapter5(story):
    _DIFF.update({'1': '中等', '2': '中等', '3': '简单'})
    story.extend(h1_block('第五章 第 1 周：架构与训练实验'))
    story.append(P(
        '本周目标是把「模型架构」20 题与「模型训练」11 题中的核心概念从纸面搬进代码。'
        '周一至周二精读模型架构模块的重点题（注意力机制、位置编码、归一化、GQA/MQA），'
        '周三至周四完成实验 1 与实验 2，周五精读模型训练模块并完成实验 3，周末复盘。'
        '本周的三个实验构成一个递进链：手写注意力是理解一切的基础，KV Cache 实验'
        '把「为什么 Decoder-only 快」量化，训练动力学实验则解释「训练为什么这样配参」。'))

    # ============ 实验 1 ============
    story.extend(h2_block('实验 1：手写 Multi-Head Attention 与 RoPE'))
    _exp_header(story, '1', '手写 MHA 与 RoPE',
                 'MHA 原理 / RoPE 旋转位置编码 / 因果掩码（对应模型架构模块 3-5 题）', '2-3 小时')
    story.append(P(
        '不用任何高层封装，仅以 PyTorch 基础算子实现多头自注意力与旋转位置编码，'
        '并用 transformers 官方实现的输出做一致性校验。完成本实验后，'
        '「Scaled Dot-Product Attention 为什么除以根号 d」「RoPE 如何把相对位置'
        '编码进点积」「因果掩码在上三角的哪一侧」这类高频追问将不再是背诵，而是回忆。'))
    story.extend(h3_block('步骤'))
    story.extend(bullets([
        '第 1 步：定义超参 d_model=512、n_heads=8、seq_len=16、batch=2，随机生成 q/k/v；',
        '第 2 步：实现 single_head_attention(q,k,v,mask)，先手写单头版本并验证 softmax 缩放；',
        '第 3 步：扩写成 MHA 类，拆分头维度、并行计算、拼接输出与输出投影；',
        '第 4 步：实现 rope(x, pos)，按奇偶列配对做旋转，注入 q 与 k（不注入 v）；',
        '第 5 步：与 HF 官方实现对比：同权重下最大误差应小于 1e-4 量级；',
        '第 6 步：（选做）把 GQA 改造进自己的实现，对比参数量与输出形状。',
    ]))
    story.extend(code_block(
        'import torch, torch.nn as nn, math\n'
        'def rope(x, base=10000.0):          # x: [B,H,L,D]\n'
        '    L, D = x.shape[-2], x.shape[-1]\n'
        '    inv = 1.0 / (base ** (torch.arange(0, D, 2).float() / D))\n'
        '    t = torch.arange(L).float()\n'
        '    freqs = torch.outer(t, inv)                  # [L, D/2]\n'
        '    cos, sin = freqs.cos(), freqs.sin()\n'
        '    x1, x2 = x[..., 0::2], x[..., 1::2]          # 奇偶配对\n'
        '    return torch.stack([x1*cos - x2*sin, x1*sin + x2*cos], -1)\n'
        '    .flatten(-2)                                # 还原维度\n'
        '\n'
        'class MHA(nn.Module):\n'
        '    def __init__(self, d=512, h=8):\n'
        '        super().__init__()\n'
        '        self.h, self.dk = h, d // h\n'
        '        self.wq, self.wk, self.wv = (nn.Linear(d, d) for _ in range(3))\n'
        '        self.wo = nn.Linear(d, d)\n'
        '    def forward(self, x, causal=True):\n'
        '        B, L, _ = x.shape\n'
        '        q, k, v = (w(x).view(B, L, self.h, self.dk).transpose(1, 2)\n'
        '                   for w in (self.wq, self.wk, self.wv))\n'
        '        q, k = rope(q), rope(k)                  # 只注入 q/k\n'
        '        att = q @ k.transpose(-2, -1) / math.sqrt(self.dk)\n'
        '        if causal:\n'
        '            att = att.masked_fill(\n'
        '                torch.triu(torch.ones(L, L, dtype=torch.bool), 1), -1e9)\n'
        '        y = (att.softmax(-1) @ v).transpose(1, 2).reshape(B, L, -1)\n'
        '        return self.wo(y)',
        label='实验 1 核心代码骨架（RoPE + MHA）'))
    story.append(callout_box(
        '检查点',
        '与 HF 实现逐元素对比误差小于 1e-4；去掉 RoPE 后对比长度外推效果'
        '（用 L=16 训练位置、L=64 推理位置观察注意力分布漂移）；'
        '把 n_heads 从 8 改为 2（模拟 MQA 极端情况）记录 KV 缓存量变化，'
        '为实验 2 埋下伏笔。'))

    # ============ 实验 2 ============
    story.extend(h2_block('实验 2：KV Cache 实现与加速比测量'))
    _exp_header(story, '2', 'KV Cache',
                 'KV Cache 原理 / GQA 与 KV 复用（对应 arch-kv-cache-q0051 图解）', '1-2 小时')
    story.append(P(
        '先看仓库中「KV Cache」一题的图解建立直觉：自回归解码时每步只需新算一个 token 的 '
        'K/V，历史部分缓存复用。本实验在自己实现的最小 GPT 上分别测量「带缓存」与'
        '「不带缓存」的逐步解码延迟，把仓库摘要里的结论「复杂度从序列长度的平方级'
        '降为线性级」变成亲手测出的数字。'))
    story.extend(h3_block('步骤'))
    story.extend(bullets([
        '第 1 步：复用实验 1 的 MHA，组装一个 4 层、d=256 的最小 decoder；',
        '第 2 步：实现 generate(model, ids, use_cache)：无缓存版每步重算全部前缀注意力；'
        '缓存版维护 past_k/past_v 列表，每步只拼新增量；',
        '第 3 步：生成 128 个 token，逐步记录两种模式的耗时与峰值显存；',
        '第 4 步：绘制「序列位置 - 累计耗时」曲线，计算加速比；',
        '第 5 步：改 n_kv_heads 为 n_heads 的一半，观察 GQA 下缓存体积减半的效果。',
    ]))
    story.extend(code_block(
        'def forward(self, x, past=None):        # past: [(k,v), ...] 每层\n'
        '    present, h = [], x\n'
        '    for i, blk in enumerate(self.blocks):\n'
        '        k_new, v_new = blk.project_kv(h)\n'
        '        if past is not None:            # 拼接历史缓存\n'
        '            k = torch.cat([past[i][0], k_new], dim=2)\n'
        '            v = torch.cat([past[i][1], v_new], dim=2)\n'
        '        else:\n'
        '            k, v = k_new, v_new\n'
        '        present.append((k, v))\n'
        '        h = blk.attend(h, k, v)         # 只对最后一个位置算 q\n'
        '    return h, present                   # present 传回下一步',
        label='实验 2 关键：增量解码的缓存拼接'))
    story.append(callout_box(
        '检查点',
        '128 token 生成时加速比应达到 3 倍以上且随长度增长继续扩大；'
        '无缓存版耗时曲线应近似随位置线性增长（每步重算全程注意力），'
        '缓存版每步耗时应近似恒定；GQA 改造后 KV 缓存张量的显存占用应减半。'
        '若数字不符，优先检查因果掩码是否被错误地缓存。'))

    # ============ 实验 3 ============
    story.extend(h2_block('实验 3：训练动力学小消融'))
    _exp_header(story, '3', '训练动力学',
                 '学习率预热、梯度累积、混合精度（对应模型训练模块 3-4 题）', '1.5 小时')
    story.append(P(
        '在 TinyShakespeare 字符级语言模型（约 1M 参数，T4 训练 10 分钟内完成）上做三组对照：'
        '有/无学习率预热、batch 累积 1 倍与 8 倍、FP32 与混合精度，'
        '观察损失曲线与吞吐差异。这个实验的价值在于：当面试官问「为什么大模型训练要用'
        '预热」「梯度累积为什么等价于大 batch」时，您能报出自己测出的数字。'))
    story.extend(table_with_caption(
        data_table(
            ['消融组', '变量', '观察指标', '预期现象'],
            [
                ['A 预热', 'warmup_steps = 0 / 500', '前 1000 步损失曲线',
                 '无预热初期震荡更大，甚至发散'],
                ['B 梯度累积', 'accum = 1 / 8', '同损失水平所需步数与吞吐',
                 '累积 8 倍后有效 batch 变大，曲线更平滑，吞吐略降'],
                ['C 混合精度', 'fp32 / bf16', '每秒步数与显存峰值',
                 'bf16 吞吐提升约 1.5-2 倍，显存约降三成'],
            ],
            ratios=[0.14, 0.24, 0.30, 0.32], fontsize=8.5),
        '表 7  实验 3 消融设计（三组独立对照）'))

    story.extend(h2_block('本周打卡与自测'))
    story.append(P(
        '周六复盘：把三个实验的输出整理进学习仓库；周日自测：遮住答案，'
        '口头回答模型架构模块的 20 题（重点：MHA 的缩放原因、RoPE 相对位置性、'
        'Pre-Norm 与 Post-Norm 的取舍、Decoder-only 为何成为主流），'
        '每题录音 60 秒回听一次，标注不流畅的题目进 Anki。'))


def chapter6(story):
    _DIFF.update({'4': '中等', '5': '中等', '6': '简单', '7': '挑战'})
    story.extend(h1_block('第六章 第 2 周：RAG 全链路实验'))
    story.append(P(
        '本周覆盖仓库中题量第二大的板块——检索增强（23 题）。四个实验串成一条完整链路：'
        '实验 4 搭出「切块、向量化、检索、生成」的基线；实验 5 在检索端做混合召回优化；'
        '实验 6 在重排端做质量提升；实验 7 把平面语料升级为知识图谱。'
        '所有实验共用同一个自建的小型中文语料（建议从仓库自身的 14 个模块文档构建——'
        '「用 RAG 学 RAG」，语料现成且答案可验证），这会让调试时的正确与否一目了然。'))

    # ============ 实验 4 ============
    story.extend(h2_block('实验 4：搭建迷你 RAG 基线'))
    _exp_header(story, '4', '迷你 RAG',
                 'RAG 三阶段链路 / Chunking 取舍（对应 rag-q0630 图解）', '2-3 小时')
    story.extend(h3_block('步骤'))
    story.extend(bullets([
        '第 1 步：语料准备——克隆仓库，把 modules/*.md 逐段切成 200 字左右的块，保留模块名元数据；',
        '第 2 步：用 sentence-transformers 的 bge-small-zh-v1.5 把全部块编码入库 FAISS；',
        '第 3 步：检索函数 top_k=5，余弦相似度；',
        '第 4 步：用 Qwen2.5-0.5B-Instruct 做生成，prompt 中拼接检索片段并要求引用；',
        '第 5 步：准备 20 个关于仓库内容的问题作为测试集，人工标注答案是否被检索片段覆盖。',
    ]))
    story.extend(code_block(
        'from sentence_transformers import SentenceTransformer\n'
        'import faiss, numpy as np, torch\n'
        'from transformers import AutoModelForCausalLM, AutoTokenizer\n'
        '\n'
        'enc = SentenceTransformer("BAAI/bge-small-zh-v1.5")\n'
        'chunks = split_modules("repo-llm-interview/modules")   # 200字/块\n'
        'emb = enc.encode(chunks, normalize_embeddings=True)\n'
        'index = faiss.IndexFlatIP(emb.shape[1])               # 内积=余弦\n'
        'index.add(emb.astype("float32"))\n'
        '\n'
        'def rag_answer(q, k=5):\n'
        '    qe = enc.encode([q], normalize_embeddings=True).astype("float32")\n'
        '    _, idx = index.search(qe, k)                      # 检索\n'
        '    ctx = "\\n".join(f"[{i+1}] {chunks[j]}" for i, j in enumerate(idx[0]))\n'
        '    prompt = f"仅依据以下资料回答，标注引用编号。\\n{ctx}\\n问：{q}\\n答："\n'
        '    ids = tok(prompt, return_tensors="pt").to("cuda")\n'
        '    out = llm.generate(**ids, max_new_tokens=200)     # 生成\n'
        '    return tok.decode(out[0][ids.input_ids.shape[1]:], True)',
        label='实验 4 核心：检索增强生成主循环'))
    story.append(callout_box(
        '检查点',
        '20 个测试问题中至少 16 个的答案可在检索片段中找到依据；'
        '故意把 top_k 从 5 降到 1，观察覆盖率下降幅度——这就是重排与混合检索的改进空间。'))

    # ============ 实验 5 ============
    story.extend(h2_block('实验 5：混合检索与 RRF 融合'))
    _exp_header(story, '5', '混合检索',
                 'BM25 与稠密互补 / RRF 名次融合（对应 rag-q0052 图解）', '2 小时')
    story.append(P(
        'BM25 抓词面精确匹配（术语、代号），稠密向量抓语义改写，两者天然互补。'
        '本实验在实验 4 的语料上建立 BM25 索引，用倒数名次融合（RRF）合并两路召回，'
        '量化对比三种方式的 Recall@10——对应仓库图解「混合检索怎么提升 RAG 召回」的结论。'))
    story.extend(code_block(
        'from rank_bm25 import BM25Okapi\n'
        'tokenized = [list(c) for c in chunks]        # 中文按字切分\n'
        'bm25 = BM25Okapi(tokenized)\n'
        '\n'
        'def hybrid_search(q, k=10, rrf_k=60):\n'
        '    dense = index.search(enc.encode([q],\n'
        '        normalize_embeddings=True).astype("float32"), k)[1][0]\n'
        '    sparse = np.argsort(bm25.get_scores(list(q)))[::-1][:k]\n'
        '    rank = {}                                # RRF 名次融合\n'
        '    for doc_ids in (dense, sparse):\n'
        '        for r, d in enumerate(doc_ids):\n'
        '            rank[d] = rank.get(d, 0) + 1.0 / (rrf_k + r + 1)\n'
        '    return sorted(rank, key=rank.get, reverse=True)[:k]',
        label='实验 5 核心：BM25 + 稠密 + RRF 融合'))
    story.append(callout_box(
        '检查点',
        '在测试集上分别计算三路 Recall@10：仅稠密、仅 BM25、混合融合。'
        '典型结果为混合比单路提升 5 至 15 个百分点；'
        '重点观察「术语精确」类问题（如某题编号、某模型名）由 BM25 救回、'
        '「语义改写」类问题由稠密向量救回的分工现象。'))

    # ============ 实验 6 ============
    story.extend(h2_block('实验 6：Reranker 对比实验'))
    _exp_header(story, '6', 'Reranker',
                 'bi-encoder vs cross-encoder / 重排收益边界（对应 rag-q0117）', '1.5 小时')
    story.append(P(
        '双塔模型（bi-encoder）牺牲精度换速度，交叉编码器（cross-encoder）把 query 与文档'
        '拼接送入同一网络，精度更高但无法预计算。本实验用 bge-reranker-base 对实验 5 的'
        '前 20 名候选重排，取前 5，对比重排前后的 nDCG@5；同时统计重排的额外时延，'
        '建立「精度换时延」的直觉。检查点：重排后 nDCG@5 提升应在 5 个百分点以上，'
        '单条重排时延在 10 毫秒量级；思考题：为什么重排只作用于前 20 名而不是全库？'))

    # ============ 实验 7 ============
    story.extend(h2_block('实验 7：GraphRAG 迷你演示'))
    _exp_header(story, '7', 'GraphRAG',
                 '实体抽取 / 图检索 vs 向量检索（对应 rag-q0009 图解）', '3-4 小时（挑战）')
    story.append(P(
        '这是本周的挑战实验，允许只完成最小闭环。流程：用 Qwen-0.5B 从每块语料中抽取'
        '「实体-关系-实体」三元组（用两三个 few-shot 示例即可驱动），入 networkx 图；'
        '查询时先定位问题实体，再取其两跳邻域作为上下文，与向量检索的结果对比。'
        '选择一个需要跨章节推理的问题（例如「注意力机制同时出现在哪些模块的题目里」），'
        '验证图检索在多跳问题上的优势；如时间不足，可用 LightRAG 等现成框架替代自建，'
        '把精力留给观察其与朴素 RAG 的差异。'))

    story.extend(h2_block('本周打卡与自测'))
    story.append(P(
        '周六：整理「召回率对比表」（三路检索 + 重排）发布到学习仓库，这张表是面试中'
        '讲述 RAG 优化的最好素材；周日：自测 RAG 板块 23 题，重点包括 RAG 与微调的边界、'
        'chunk 大小的权衡、评估指标 Recall/忠实度/答案相关性三件套。'))


def chapter7(story):
    _DIFF.update({'8': '中等', '9': '挑战', '10': '中等'})
    story.extend(h1_block('第七章 第 3 周：微调与对齐实验'))
    story.append(P(
        '本周覆盖「模型微调」4 题与「RLHF 与对齐」8 题，共 12 题，是四周中阅读量最轻、'
        '但实验深度最重的一周。T4 的 16GB 显存决定了我们必须用 0.5B 级模型与 QLoRA 路线，'
        '这恰好也是业界在小卡上做微调的标准姿势——面试中完全成立。'
        '实验 8 做 SFT 式指令微调，实验 9 做 DPO 偏好对齐，实验 10 统一评估，'
        '三者构成一条完整的「预训练模型变成可用助手」的最小流水线。'))

    # ============ 实验 8 ============
    story.extend(h2_block('实验 8：QLoRA 指令微调'))
    _exp_header(story, '8', 'QLoRA',
                 'LoRA 低秩分解 / rank 与 alpha / 冻结主干（对应 train-q0205 图解）', '3-4 小时')
    story.append(P(
        '用 4 比特量化加载 Qwen2.5-0.5B-Instruct，在其上训练 LoRA 适配器，'
        '让模型学会用固定格式回答仓库题目的 30 秒摘要风格。'
        '训练数据无需标注成本：把 74 道 B 级题的「题面 → 30 秒回答」直接作为指令对，'
        '再从官网风格模板扩展几个系统提示即可，约百条样本就足以让模型学会格式。'))
    story.extend(h3_block('步骤'))
    story.extend(bullets([
        '第 1 步：构造数据集 questions.jsonl，字段为 instruction 与 output；',
        '第 2 步：BitsAndBytesConfig 以 nf4 双量化加载基座模型，并开启计算_dtype=bfloat16；',
        '第 3 步：LoraConfig(r=8, alpha=16, target_modules=[q_proj,k_proj,v_proj,o_proj])；',
        '第 4 步：SFTTrainer 训练 3 个 epoch，batch=2，累积 8，学习率 2e-4；',
        '第 5 步：保存适配器，对比「合并前推理」与「merge_and_unload 后推理」；',
        '第 6 步：打印 trainable_parameters 百分比，对照图解中「只训练 A、B」的说法。',
    ]))
    story.extend(code_block(
        'from transformers import AutoModelForCausalLM, BitsAndBytesConfig\n'
        'from peft import LoraConfig, get_peft_model, prepare_model_for_kbit\n'
        'import torch\n'
        '\n'
        'bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",\n'
        '        bnb_4bit_compute_dtype=torch.bfloat16)   # QLoRA 双量化\n'
        'model = AutoModelForCausalLM.from_pretrained(\n'
        '    "Qwen/Qwen2.5-0.5B-Instruct", quantization_config=bnb,\n'
        '    device_map="auto")\n'
        'model = prepare_model_for_kbit_training(model)\n'
        'peft_model = get_peft_model(model, LoraConfig(\n'
        '    r=8, lora_alpha=16, lora_dropout=0.05,        # 秩与缩放\n'
        '    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],\n'
        '    task_type="CAUSAL_LM"))\n'
        'peft_model.print_trainable_parameters()\n'
        '# 典型输出: trainable 0.9% || trainable 3.4M / 391M total',
        label='实验 8 核心：QLoRA 装配'))
    story.append(callout_box(
        '检查点',
        '可训练参数占比应在 1% 量级；微调后模型能以「一句话 + 结论先行」的风格回答训练过的题目；'
        '把 r 改为 16 与 32 各跑一次，观察损失几乎没有差异——这正是图解里'
        '「低秩假设成立」的证据；记录 T4 上的显存峰值（应在 8GB 以内）。'))

    # ============ 实验 9 ============
    story.extend(h2_block('实验 9：DPO 偏好对齐（最小实现）'))
    _exp_header(story, '9', 'DPO',
                 'DPO 与 PPO 的链路差异 / 偏好数据（对应 rl-q0076 图解）', '3 小时（挑战）')
    story.append(P(
        '仓库图解对 DPO 与 PPO 的对比结论是：PPO 依赖在线采样、奖励模型与价值估计的闭环，'
        'DPO 直接从离线偏好对学习，工程链路更短。本实验亲手验证「链路更短」：'
        '用 TRL 的 DPOTrainer 在自造的 200 条偏好对（chosen 为格式规范的回答，'
        'rejected 为同一模型未微调时的啰嗦输出）上训练实验 8 的适配器。'
        '若显存吃紧，可把 r 降为 4 或直接对 0.5B 基座做 DPO。'
        '检查点：训练后 chosen 与 rejected 的隐式奖励差（logps 差）应显著拉开；'
        '在追问「DPO 为什么不需要 reward model」时，能画出其从'
        '偏好概率到最优策略的闭式推导草图。'))
    story.extend(code_block(
        'from trl import DPOTrainer, DPOConfig\n'
        '# dataset 字段: prompt / chosen / rejected 三列\n'
        'trainer = DPOTrainer(\n'
        '    model=peft_model,                       # 延续实验8的适配器\n'
        '    args=DPOConfig(\n'
        '        per_device_train_batch_size=1, gradient_accumulation_steps=16,\n'
        '        learning_rate=5e-5, num_train_epochs=1, bf16=True),\n'
        '    train_dataset=dpo_ds, processing_class=tokenizer)\n'
        'trainer.train()                             # 无需奖励模型',
        label='实验 9 核心：DPO 训练器'))

    # ============ 实验 10 ============
    story.extend(h2_block('实验 10：微调效果系统评估'))
    _exp_header(story, '10', '微调评估',
                 '离线评测 / 困惑度与小测试集（对应评估与监控模块 2-3 题）', '1.5 小时')
    story.append(P(
        '从仓库 100 题中留出 20 题作为「考试卷」（不参与实验 8 训练），'
        '对微调前后的模型做三方面对比：一是答案格式合格率（是否结论先行、是否分点）；'
        '二是用 GLM-4 或 GPT 类大模型做五分制评分的均值（这一步可留到第 4 周用评测集统一做）；'
        '三是推理延迟是否变化（LoRA 合并后应几乎无差）。'
        '把结果整理成「微调前 vs 微调后」对照表，这就是简历上「基于开源题库完成'
        'QLoRA 微调与评估闭环」的原始证据。'))

    story.extend(h2_block('本周打卡与自测'))
    story.append(P(
        '周六：把实验 8 至 10 的模型卡片、超参与对照表写入学习仓库；'
        '周日：自测微调与对齐 12 题，重点：LoRA 为什么比全量微调整体更省但单步未必更快、'
        'PEFT 方法族谱（前缀、适配器、重参数化）、PPO/DPO/GRPO 三者取舍、'
        '灾难性遗忘的缓解手段。'))


def chapter8(story):
    _DIFF.update({'11': '中等', '12': '简单', '13': '挑战'})
    story.extend(h1_block('第八章 第 4 周：Agent、推理优化与 LLM 评测'))
    story.append(P(
        '最后一周覆盖剩余五个模块共 34 题，实验焦点从「模型能力」转向「工程与产品化」。'
        '实验 11 实现 Agent 的规划-工具-记忆闭环；实验 12 量化推理压榨部署性能；'
        '实验 13 是整个月的旗舰——把仓库 100 题转化为中文 LLM 评测集并产出首份评测报告，'
        '它同时是您「二次开发」目标的落地物。多模态 8 题以精读图解为主'
        '（Colab 免费额度跑视觉实验性价比低），可选用 Qwen2-VL-2B 做一次图片描述演示。'))

    # ============ 实验 11 ============
    story.extend(h2_block('实验 11：ReAct Agent 与工具调用'))
    _exp_header(story, '11', 'ReAct Agent',
                 '规划-执行-观察循环 / 工具协议 / 停止条件（对应 rag-q0513 图解）', '2-3 小时')
    story.append(P(
        '按仓库 Agent 图解的四组件搭建一个能回答「仓库里某题目讲什么」的问答 Agent：'
        '工具一为检索（复用实验 4 的 FAISS 索引），工具二为计算器（验证多工具选择），'
        '记忆用列表保存最近三轮对话。核心是 ReAct 循环：模型输出思考与动作，'
        '执行工具后把观察结果拼回上下文，直到模型给出最终答案或触发步数上限——'
        '这个「停止条件」正是图解强调的可靠性要素之一。'))
    story.extend(code_block(
        'TOOLS = {\n'
        '  "search_repo": {"desc": "在题库中检索相关内容",\n'
        '                  "args": ["query: str"]},\n'
        '  "calculator": {"desc": "四则运算", "args": ["expr: str"]}}\n'
        'PROMPT = """按 ReAct 循环工作，每次输出一行 JSON：\n'
        '{{"thought": ..., "action": "工具名或finish",\n'
        '  "input": ..., "answer": ...}}\\n可用工具: {tools}\\n历史: {memory}\\n问题: {q}"""\n'
        '\n'
        'def agent_loop(q, max_steps=5):\n'
        '    memory = []\n'
        '    for _ in range(max_steps):                  # 停止条件\n'
        '        out = llm_json(PROMPT.format(\n'
        '            tools=TOOLS, memory=memory[-3:], q=q))\n'
        '        if out["action"] == "finish":\n'
        '            return out["answer"]\n'
        '        obs = run_tool(out["action"], out["input"])\n'
        '        memory.append((out["thought"], out["action"], obs))\n'
        '    return "达到步数上限，请换一种问法"            # 失败处理',
        label='实验 11 核心：ReAct 循环骨架'))
    story.append(callout_box(
        '检查点',
        'Agent 应能对「KV Cache 一题引用了哪些论文」类问题自主选择检索工具并给出'
        '带出处的回答；构造一个需要两跳的问题验证多步规划；'
        '故意提供错误工具名，验证模型的重试或澄清行为；统计平均步数（应在 2-3 步）。'))

    # ============ 实验 12 ============
    story.extend(h2_block('实验 12：量化推理 Benchmark'))
    _exp_header(story, '12', '量化',
                 '量化为什么不掉点 / int8 vs int4 吞吐（对应推理优化模块 2-3 题）', '1.5 小时')
    story.append(P(
        '用 bitsandbytes 对 Qwen2.5-0.5B 分别以 fp16、int8、int4 加载，'
        '各生成 200 个 token，记录首 token 时延、每秒 token 数、显存峰值与'
        '生成文本的困惑度差异。检查点：int4 相对 fp16 显存约省 60% 至 70%，'
        '吞吐因反量化开销可能不升反降（这点常被误解）；困惑度劣化应控制在小幅范围；'
        '把结果画成四指标雷达图。延伸思考：GPTQ/AWQ 与bnb量化的区别可只读论文摘要，'
        '面试答出「训练后量化 vs 训练中量化」的分层即可。'))

    # ============ 实验 13 ============
    story.extend(h2_block('实验 13（旗舰）：构建 LLM 评测集与首份评测报告'))
    _exp_header(story, '13', 'LLM 评测',
                 '全仓库 14 模块考点 / B 级参考答案（综合运用全部知识）', '4-5 小时（挑战）')
    story.append(P(
        '本实验把整月所学收敛为一个可展示的项目：解析仓库为结构化评测集，'
        '批量测试一个模型（推荐 GLM 系列，OpenAI 兼容接口也可），'
        '产出按模块分组的得分报告。评测维度建议三选二：格式规范性（是否结论先行、分点）、'
        '事实正确性（与 B 级参考答案的要点覆盖，用大模型当裁判）、'
        '追问鲁棒性（对同一题换三种问法，答案是否一致）。'))
    story.extend(h3_block('第 1 步：解析仓库为 JSONL'))
    story.extend(code_block(
        'import re, json, pathlib\n'
        '\n'
        'def parse_module(md_path):\n'
        '    text = pathlib.Path(md_path).read_text(encoding="utf-8")\n'
        '    module = re.match(r"# (.+?)图解", text).group(1)\n'
        '    for sec in re.split(r"\\n### ", text)[1:]:\n'
        '        head, body = sec.split("\\n", 1)\n'
        '        q = head.split(". ", 1)[1].rstrip("?？") + "?"\n'
        '        ans = re.search(r"\\*\\*30 秒回答：\\*\\* (.+)", body)\n'
        '        tier = "B" if "来源等级：** B" in body else "C"\n'
        '        refs = re.findall(r"arxiv.org/abs/([\\d.]+)", body)\n'
        '        yield {"module": module, "question": q,\n'
        '               "ref": ans.group(1) if ans else "",\n'
        '               "tier": tier, "refs": refs}\n'
        '\n'
        'with open("eval_set.jsonl", "w") as f:            # 100 行\n'
        '    for p in pathlib.Path("modules").glob("*.md"):\n'
        '        for item in parse_module(p):\n'
        '            f.write(json.dumps(item, ensure_ascii=False) + "\\n")',
        label='第 1 步：解析 modules/*.md（约 20 行核心）'))
    story.extend(h3_block('第 2 步：批量测试'))
    story.extend(code_block(
        'from z_ai import ZAI           # 或 openai SDK，接口一致\n'
        'client = ZAI()\n'
        '\n'
        'def ask(q):\n'
        '    r = client.chat.completions.create(\n'
        '        model="glm-4-flash",     # 免费模型即可起步\n'
        '        messages=[{"role": "user",\n'
        '                   "content": f"用面试口吻，结论先行，"\n'
        '                              f"120字内回答：{q}"}])\n'
        '    return r.choices[0].message.content\n'
        '\n'
        'results = []\n'
        'for item in dataset:             # eval_set.jsonl\n'
        '    results.append({**item, "answer": ask(item["question"])})\n'
        'json.dump(results, open("raw_answers.json", "w"),\n'
        '          ensure_ascii=False, indent=1)',
        label='第 2 步：批量调用被测模型'))
    story.extend(h3_block('第 3 步：裁判评分与报告'))
    story.append(P(
        '用更强模型做裁判，输入「题目、参考答案（B 级题）、被测答案」，'
        '按要点覆盖度输出零到五分。汇总后按 14 个模块与 B/C 等级分组统计均值，'
        '输出 Markdown 报告：整体得分、最弱三个模块、B 级与 C 级得分差、'
        '三处典型失败样例。至此，「用开源题库二次开发为评测集」的目标闭环完成，'
        '报告本身就是一份数据资产。检查点：解析脚本应稳定产出 100 行；'
        '评测报告应包含分组统计与样例分析两个层级；建议把随机种子与时间戳写入报告，'
        '保证可复现。'))

    story.extend(h2_block('本周打卡与总复盘'))
    story.append(P(
        '周六：发布评测集与报告至学习仓库，附 README 说明方法与局限；'
        '周日：全量 100 题最终自测，从每个模块随机抽三题做 60 秒口述录音，'
        '统计各模块口述流畅度并更新 Anki；最后花 30 分钟更新简历，'
        '把本月的「RAG 对比实验、QLoRA 微调闭环、中文 LLM 评测集」三个项目'
        '写成三行 STAR 法则描述。'))


def chapter9(story):
    story.extend(h1_block('第九章 风险建议与进阶路线'))

    story.extend(h2_block('9.1 常见坑与规避'))
    story.extend(table_with_caption(
        data_table(
            ['坑', '典型症状', '规避方法'],
            [
                ['Colab 会话回收', '长训练被中断，权重丢失',
                 'checkpoint 每 epoch 存 Drive；关键产物即存即同步'],
                ['显存 OOM', '微调时报 CUDA out of memory',
                 '按「batch、rank、序列长度」顺序降；4bit 优先；'
                 '开 gradient_checkpointing'],
                ['中文字体缺失', '图表中文变方块',
                 'matplotlib 先 addfont 再设 rcParams（见各实验骨架）'],
                ['依赖版本冲突', 'peft 与 transformers 不兼容',
                 '每实验独立笔记本；安装后重启运行时；固定版本号'],
                ['评测不可复现', '两次跑分差异大',
                 '固定 temperature=0 与随机种子；报告注明版本与时间'],
                ['仓库内容过期', '上游更新后图解变化',
                 '本地克隆锁定 commit；引用时注明复核日期'],
            ],
            ratios=[0.17, 0.30, 0.53], fontsize=8.5),
        '表 8  六个高频坑与规避手段'))

    story.extend(h2_block('9.2 时间不足时的裁剪优先级'))
    story.append(P(
        '若每周可用时间不足 7 小时，按以下顺序裁剪：先砍实验 7（GraphRAG，'
        '改读 LightRAG 文档替代）；再砍实验 9（DPO，改为精读图解与论文）；'
        '再把实验 6 并入实验 5（只跑重排一次对比）。以下三项是底线，任何情况下保留：'
        '实验 1（手写注意力，原理基石）、实验 4（RAG 链路，应用岗高频）、'
        '实验 8（QLoRA 微调，差异化证据）。若只剩一周，就只做这三个实验加'
        '全量题目的三层阅读。'))

    story.extend(h2_block('9.3 与求职的衔接'))
    story.append(P(
        '一个月后的面试叙事线建议这样组织：开场用「我系统评测过一个开源题库并构建了'
        '中文 LLM 评测集」建立记忆点；原理层用实验 1 至 3 的数字支撑'
        '（例如「我实测 KV Cache 在 128 token 时带来 3 倍以上加速」）；'
        '应用层用实验 4 至 7 的对比表讲述 RAG 优化方法论'
        '（「混合检索把 Recall@10 提升了若干个点」）；工程层用实验 8 至 12 讲'
        '成本与性能权衡（「int4 显存省六成但吞吐反降」这类反直觉结论最加分）。'
        '每条经历都遵循 STAR 结构：仓库题目是情境与任务，本手册实验是行动，'
        '数字化的检查点是结果。'))
    story.append(P(
        '面试临考前一周，把 Anki 里到期卡片刷完两轮，重点复习标注掌握度低于三分的题目；'
        '口述录音回听两遍，修正「嗯、然后」等口语赘词；'
        '对最弱两个模块，回到仓库精读图解与参考论文，'
        '用官网完整答案的口语讲法校准自己的表达节奏。'))

    story.extend(h2_block('9.4 后续进阶路线'))
    story.extend(bullets([
        '<b>姊妹项目：</b>作者维护的 RAG From Zero 教程是第 2 周的天然延伸，'
        '可按周计划逐篇复现，与本手册实验互为印证；',
        '<b>推理部署：</b>用 vLLM 起一个本地服务，把实验 12 的 benchmark 从'
        '单条推理升级为并发压测（吞吐、P99 时延），对应推理优化模块的剩余考点；',
        '<b>完整对齐：</b>在 24GB 以上显卡上把实验 9 扩展为「奖励模型训练 + PPO 完整链路」，'
        '或用 TRL 的 GRPOTrainer 复现 GRPO，对齐仓库 RLHF 模块的前沿考点；',
        '<b>评测深耕：</b>把评测集扩展为公开数据集（附论文级技术报告），'
        '或在内部团队复用为回归测试集，让这份二次开发产出持续产生价值。',
    ]))
