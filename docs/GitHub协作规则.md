# GitHub 协作规则

> **适用范围**：本仓库内全部代码与文档协作流程，自 GitHub 连接建立起对所有后续操作生效。
> **状态**：GitHub 地址与 token 均已同步（2026-10-25），仓库已建立连接；详见 [四、连接信息](#四连接信息)。
> **最后更新**：2026-10-25

## 一、规则总览

| # | 规则 | 约束要点 |
|---|------|----------|
| 1 | 唯一同步方式 | 所有代码/文档改动通过 `git commit` + `git push` 推送到 GitHub，不在对话中凭空产生代码 |
| 2 | 仓库位置 | 严格使用指定仓库目录（待回填），不在其他目录创建 `.git` |
| 3 | 提交规范 | 小步提交，commit message 使用 Conventional Commits 风格（如 `feat:`、`fix:`、`docs:`） |
| 4 | 会话记录 | 分析/评估/测试记录写入 `docs/` 目录，以 Markdown 形式提交推送 |
| 5 | 禁止 force push | 绝不使用 `git push --force`；禁止对已推送 commit 执行 `--amend` 后再推送（等效 force）；未推送 commit 的 amend 属常规修正手段，不受限 |
| 6 | Rebase 前置 | rebase 前先评估替代方案（revert / merge），必要时提前告知确认 |
| 7 | bug 修复不重命名变量 | 修复 bug 时保持原变量名，仅在 refactor 时重命名 |

## 二、规则详解

### 1. 唯一同步方式

一切代码与文档改动均以「落地为文件 → `git add` → `git commit` → `git push`」的链路同步到 GitHub。对话中给出的产出若未进入仓库，视为未交付；最终内容以仓库为准，仓库即唯一事实来源（single source of truth）。

执行要点：

- 任何脚本、文档、配置的修改都发生在仓库目录内的文件上，随后提交推送；
- 对话中的代码片段只是中间态，最终以推送后的仓库内容为准；
- 由此保证全部改动可回溯、可 diff、可 revert。

### 2. 仓库位置

- **本地仓库根目录：`/home/z/my-project/repo-llm-interview/`**（唯一允许存在 `.git` 的目录）；
- **GitHub 远端（origin）：`https://github.com/dongf9527/llm-interview-questions.git`**；
- 仅允许在上述目录内进行 git 操作，禁止在项目内其他任何子目录或无关目录执行 `git init`、创建 `.git`；
- 目的：避免 `.git` 散落导致的仓库嵌套（nested repository）、误初始化与同步混乱；
- 仓库基线：本地已含上游 `MisterBooo/llm-interview-questions` main 分支全部内容（CC BY-SA 4.0，保留原 LICENSE 与作者署名），作为二次开发的基础。

### 3. 提交规范

小步提交：一次 commit 只聚焦一件事（一个功能、一个修复或一组紧密相关的文档更新），避免大杂烩式提交。commit message 遵循 Conventional Commits 风格：`<type>: <简短描述>`。

常用类型速查：

| type | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 新增实验13评测集构建脚本` |
| `fix` | 缺陷修复 | `fix: 修复 CJK 行首标点禁则缺失` |
| `docs` | 文档变更 | `docs: 添加 GitHub 协作规则` |
| `style` | 格式调整（不影响逻辑） | `style: 统一缩进为 4 空格` |
| `refactor` | 重构（非新功能、非修复） | `refactor: 抽取公共字体注册逻辑` |
| `test` | 测试相关 | `test: 补充分词禁则用例` |
| `chore` | 构建/工具/杂项 | `chore: 更新 .gitignore` |

### 4. 会话记录

分析、评估、测试等过程性记录统一以 Markdown 形式写入 `docs/` 目录，与代码同等对待地提交推送。

执行要点：

- 记录内容：项目评估结论、实验过程与结果、问题排查记录等；
- 文件名建议自解释（主题明确，必要时带日期）；
- 记录随产生随提交，不积压到会话结束。

### 5. 禁止 force push

绝不使用 `git push --force`（含 `-f` 等一切改写远端历史的推送参数）。同理，**对已推送的 commit 执行 `--amend` 后再推送**与 force push 等效，同样禁止。对尚未推送的本地 commit 执行 `--amend` 修正笔误属常规手段，不受本条限制。

| 场景 | 正确做法 | 禁止做法 |
|------|----------|----------|
| 同步日常改动 | `commit` + `push` | 产出停留在对话中不入库 |
| 修正未推送 commit 笔误 | `git commit --amend` 后正常 push | ——（允许） |
| 修改已推送内容 | 新增 `fix:` / `docs:` commit，或 `git revert` | `--amend` 后再推、任何形式的 force push |
| 回滚已推送改动 | `git revert <commit>` | `reset --hard` 后强推远端 |

### 6. Rebase 前置

rebase 会改写提交历史，执行前必须先评估替代方案：

- `git revert`：以反向提交撤销改动，不改写历史，默认首选；
- `git merge`：保留双方原始历史，适合整合分支。

确需 rebase（含交互式 rebase 整理未推送 commit）时，先说明意图与影响范围，必要时获得确认后再执行；不在未告知的情况下改写任何历史。

### 7. bug 修复不重命名变量

修复 bug 时保持原有变量名/函数名不变，使 diff 只包含逻辑修复本身；重命名属于 refactor 范畴，仅在重构时进行，并单独提交。

执行要点：

- fix 的 diff 保持最小化，便于 review 与回溯定位；
- 若修 bug 过程中确需重命名，拆分为独立的 `refactor:` commit，不与 `fix:` 混杂；
- 示例：`fix: 修正 story.extend 误用导致的排版错误`（保持原名）→ `refactor: 统一辅助 Flowable 返回值类型`（单独提交）。

## 三、凭证安全约定

GitHub 访问 token 仅用于本地/会话内的远端认证（如 credential 配置或 remote URL），**严禁写入任何被提交的文件**（代码、文档、配置、日志）。若发现 token 意外入库：立即在 GitHub 侧吊销并更换；历史清理涉及改写远端，须先按规则 5、6 评估并确认后进行。

## 四、连接信息

- [x] GitHub 远端地址：`https://github.com/dongf9527/llm-interview-questions.git`（2026-10-25 同步）
- [x] 本地仓库根目录：`/home/z/my-project/repo-llm-interview/`（唯一 `.git` 所在地）
- [x] 远端认证 token（2026-10-25 同步）：仅存于本地 `.git/credentials`（credential helper store，位于仓库 `.git/` 内、永不随提交入库），未写入任何被提交文件
- [x] 上游远端 `upstream`：`https://github.com/MisterBooo/llm-interview-questions.git`（fork 工作流标配：拉取上游更新用 fetch upstream，永不直接 push upstream）

远端基线：上游 main 完整历史（截至同步日共 8 个提交，tip `320048c`）已镜像至远端 main。
