# agentmemory Viewer 汉化补丁

> 🇨🇳 为 [agentmemory](https://github.com/rohitg00/agentmemory) 的内置 Viewer（`:3113`）提供**简体中文界面**。纯文案替换，不改任何功能逻辑，不发送任何数据。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Upstream](https://img.shields.io/badge/upstream-agentmemory%200.9.29-green)](https://github.com/rohitg00/agentmemory)

## 效果

| 原版 | 汉化后 |
|---|---|
| Sessions / Memories / Lessons / Graph / Crystals / Actions | 会话 / 记忆 / 经验 / 图谱 / 晶体 / 操作 |
| No memories yet | 暂无记忆 |
| Are you sure you want to delete... | 确定要删除 "xxx"？此操作不可撤销。 |
| Running in BM25-only mode | 正以纯 BM25 模式运行 |

覆盖范围：导航页签、仪表盘、会话详情、图谱、空状态说明（长段落）、删除确认对话框、加载提示、状态消息、枚举值（记忆类型 / 断路器状态 / 工作进程状态 / 会话状态 / 操作状态 / 回放事件类型）、搜索框 placeholder、可访问性标签、悬浮提示、动态按钮文案，共 **295 条**。语言标记同步改为 `lang="zh-CN"`。

## 快速开始

```bash
# 0. 获取补丁
git clone https://github.com/yaheng100/agentmemory-zh-cn.git
cd agentmemory-zh-cn

# 1. 检测兼容性（不改文件）
python agentmemory_i18n_patch.py check

# 2. 应用汉化（自动备份官方英文原文为 index.html.bak-en）
python agentmemory_i18n_patch.py apply

# 3. 应用「会话页布局修复」（可选，但强烈建议 —— 见下文）
python agentmemory_layout_patch.py apply

# 4. 浏览器打开 http://localhost:3113，Ctrl+F5 强制刷新即可
```

脚本会自动定位 viewer 文件（通过 `npm root -g`）；定位失败时手动指定：

```bash
python agentmemory_i18n_patch.py apply --file "C:\path\to\node_modules\@agentmemory\agentmemory\dist\viewer\index.html"
```

Windows 用户也可以直接双击 `apply.cmd` / `restore.cmd`。

## 会话页布局修复（`agentmemory_layout_patch.py`）

本仓库的第二个补丁，解决「会话」页一个很别扭的默认布局。

**问题**：会话视图是两栏布局 `minmax(300px,400px) minmax(0,1fr)`，
但**没选中任何会话时**右侧详情面板是空的，却仍占着 `1fr`。
结果会话列表被压在最多 400px 的窄栏里，右面约 **2/3 宽度全空**；
窄栏还把命令预览挤成 3~4 行折行。

**修复**：

| 场景 | 修复前 | 修复后 |
|---|---|---|
| 未选中会话 | 列表 400px 窄栏 + 右侧全空 | 铺满整行，**固定三列**卡片网格（窄屏 1100px↓ 两列、820px↓ 单列） |
| 选中会话 | 两栏 | 仍是两栏（左列表 + 右详情），只在真正需要时才分栏 |
| 会话 ID | `9881b…74d417`（省略） | 完整 UUID `9881b897-914a-418d-9485-f46bd874d417` |
| 命令预览 | 折行 3~4 行 | 裁到 2 行（`-webkit-line-clamp`） |
| 包装标签 | 直接露出 `<command-message>…` | 清洗为可读的 `/命令 参数` |

用法与汉化补丁一致：

```bash
python agentmemory_layout_patch.py check     # 检测（不改文件）
python agentmemory_layout_patch.py apply     # 应用（自动备份）
python agentmemory_layout_patch.py restore   # 回滚
```

> 实现细节：Claude Code 存下来的 `firstPrompt` 被**截断到约 200 字符**，
> 所以 `<local-command-caveat>` 常常没有闭合标签 —— 清洗函数必须有
> 「未闭合兜底」规则，否则整段英文提示会留在卡片上。

两个补丁互不依赖，可单独 `apply` / `restore`。

## 恢复英文

```bash
python agentmemory_i18n_patch.py restore
```

从 `index.html.bak-en` 备份还原，之后随时可以重新 `apply`。

## 版本适配

- ✅ 已适配：agentmemory **v0.9.29**
- ⚠️ 其他版本：先跑 `check`，命中 ≥100 条即可放心使用；命中率低说明 viewer 结构有变，欢迎提 issue 反馈版本号
- agentmemory 升级后 viewer 文件会被覆盖回英文，重新 `apply` 即可（新版本先 `check`）

## 原理

Viewer 是一个单文件 HTML（内联 CSS/JS，无外部资源）。本补丁直接对该文件做**精确字符串替换**：

1. 静态文本节点（`>Text<` 形态）
2. `title=` / `placeholder=` 属性
3. JS 模板字符串与动态拼接文案（引号锚定，避免误伤代码与 API 路径）
4. `<html lang>` 标记

记忆内容本身（你的会话观测数据）**不会被翻译**——只翻译界面框架文案。

## 已知保留项（刻意不翻）

- 品牌词 `agentmemory`（含 `agentmemory viewer ·`、页脚版本号）
- `AGENTMEMORY_SECRET`、`GRAPH_EXTRACTION_ENABLED` 等**环境变量名**
- `github` 链接文字、API 路径、demo 示例数据
- 「反馈问题」按钮生成的 **GitHub issue 正文模板**（`### What went wrong` 等）——该模板面向上游英文仓库维护者，保留英文更利于沟通
- 浏览器控制台的 `console.warn / console.error` 日志

> 说明：枚举值（记忆类型 `fact`/`architecture`、断路器状态 `open`/`closed`、操作状态 `pending`/`done` 等）
> **只翻译显示文本**，`<option value="...">`、筛选参数与入库原值一律保持英文，不影响任何功能逻辑。

## 更新记录

### 2026-09-11 新增「会话页布局修复」补丁（v2）

起因：会话页把列表锁在 400px 窄栏里，未选中会话时右侧 2/3 全空，
命令预览还被挤成 4 行折行。新增独立脚本 `agentmemory_layout_patch.py`
（`check` / `apply` / `restore`），共 5 处替换点：

1. CSS 两栏布局 → 未选中**固定三列**网格（窄屏降级 2 列/1 列）；选中才两栏
2. CSS 预览裁到 2 行（`-webkit-line-clamp`）+ `.session-meta` 加 `word-break`
3. JS 新增 `cleanSessionPreview()` + 渲染时按选中状态加 `has-detail` 类
4. JS 预览调用清洗后的文本（长度 140 → 160）
5. JS 会话 ID 由 `shortSessionId(s, 12)` 改为 `sessionId(s)`，显示完整 UUID

**版本兼容**：脚本对每个替换点带多个 `old` 变体并按长度优先匹配，所以无论
起点是上游原始文件（v0）还是上一版补丁（v1：自适应多列 + 省略 ID），
`apply` 都能一步升到 v2。

验证：隔离副本上分别验证 v0 → v2、v1 → v2、幂等、restore 全部通过；
两条路径产物 md5 均与生产文件一致；CRLF 行尾保持不变。

### 2026-09-10（第三轮）201 → 276 条

- 修复 4 处「加载中」文案从未命中：源码用的是 **Unicode 省略号 `…`（U+2026）** 且形态为 `<h3>…</h3>` / `>…</div>`，旧规则误按 ASCII `...` 加单引号锚定
- 修复「暂无观测」筛选提示：源码结尾是 `'</p></div>'`，旧规则只写到 `'</p>'`
- 修复记忆栏说明句半截汉化（"记忆 are durable facts…"）
- 补齐 `Shown: N total.`、`— click to expand`、`↻ Rebuild Graph`、`Engine connection lost — reconnecting.`、
    `% of allocated heap in use …`、`Requires an LLM provider key …` 等长句的后半段
- 枚举值汉化扩展到断路器 / 工作进程 / 会话 / 操作状态与回放事件类型（新增 `VAL_ZH` 项 29 个）
- 新增注入后 JS 语法自检与 `valZh` 断言脚本

### 2026-09-10（第四轮）276 → 295 条：headless 浏览器逐 tab 实测

用 headless Chromium 把 12 个 tab 全部真实渲染后提取可见文本，
抓到一批**静态扫描永远看不到**的运行时文案：

| 位置 | 修复前 | 修复后 |
|---|---|---|
| 头部日期 | `Thu, Sep 10, 2026` | `2026年9月10日星期四`（`toLocaleDateString('en-US')` → `zh-CN`） |
| 右上角连接状态 | `live` / `connecting...` / `polling · 30s` | `实时` / `连接中...` / `轮询 · 每 30 秒` |
| 健康 / 连接 | `healthy` / `connected` | `健康` / `已连接`（`esc()` → `valZh()`） |
| 统计卡副标题 | `0 active` / `E357 edges` / `0 functions tracked` | `0 个进行中` / `E357 条边` / `0 个函数` |
| Token 节省 | `~N tokens · $X saved` | `~N 个 token · 节省 $X` |
| 活动栏目标数 | `(25 targets)` | `(25 个目标)` |
| 审计栏目标数 | `25 target(s):` | `25 个目标：` |
| 空状态代码块注释 | `# Save a lesson explicitly` 等 4 组 | 全部中文化（命令本体保持原样） |

## 校验脚本（可选）

`apply` 之后建议跑一次，确认替换没有破坏内联 JS（需要 Node.js）：

```bash
# 1) 内联 <script> 语法自检（只解析，不执行）
node tools/check_js_syntax.js "C:\path\to\...\dist\viewer\index.html"

# 2) valZh 枚举映射断言 + 渲染点切换检查（含 CSS 类未被误改）
node tools/verify_valzh.js "C:\path\to\...\dist\viewer\index.html"

# 3) 终极复检：headless 浏览器逐 tab 真实渲染，扫出运行时才出现的英文
#    （check 只能命中静态模板字符串，看不到 JS 运行时拼出来的内容）
python tools/render_scan_i18n.py                  # 全部 12 个 tab + 截图
python tools/render_scan_i18n.py dashboard memories    # 只看指定 tab
```

前两个通过时打印 `[OK]` 并以退出码 0 结束，可直接接入 CI；
`render_scan_i18n.py` 理想结果是只剩 `agentmemory` / `github` 等品牌词。

## 安装前提

- 已安装并运行 [agentmemory](https://github.com/rohitg00/agentmemory)（`npx @agentmemory/agentmemory`）
- Python 3.8+（无第三方依赖，纯标准库）

## License

MIT。上游 [agentmemory](https://github.com/rohitg00/agentmemory) 为 Apache-2.0，本补丁仅修改本地已安装的文件，不重分发上游代码。

---

*Made with 🛢️ by [yaheng100](https://github.com/yaheng100)*
