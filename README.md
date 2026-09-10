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

覆盖范围：导航页签、仪表盘、会话详情、图谱、空状态说明（长段落）、删除确认对话框、加载提示、状态消息、枚举值（记忆类型 / 断路器状态 / 工作进程状态 / 会话状态 / 操作状态 / 回放事件类型）、搜索框 placeholder、可访问性标签、悬浮提示、动态按钮文案，共 **276 条**。语言标记同步改为 `lang="zh-CN"`。

## 快速开始

```bash
# 0. 获取补丁
git clone https://github.com/yaheng100/agentmemory-zh-cn.git
cd agentmemory-zh-cn

# 1. 检测兼容性（不改文件）
python agentmemory_i18n_patch.py check

# 2. 应用汉化（自动备份官方英文原文为 index.html.bak-en）
python agentmemory_i18n_patch.py apply

# 3. 浏览器打开 http://localhost:3113，Ctrl+F5 强制刷新即可
```

脚本会自动定位 viewer 文件（通过 `npm root -g`）；定位失败时手动指定：

```bash
python agentmemory_i18n_patch.py apply --file "C:\path\to\node_modules\@agentmemory\agentmemory\dist\viewer\index.html"
```

Windows 用户也可以直接双击 `apply.cmd` / `restore.cmd`。

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

- **2026-09-10（第三轮）** 276 条
  - 修复 4 处「加载中」文案从未命中：源码用的是 **Unicode 省略号 `…`（U+2026）** 且形态为 `<h3>…</h3>` / `>…</div>`，旧规则误按 ASCII `...` 加单引号锚定
  - 修复「暂无观测」筛选提示：源码结尾是 `'</p></div>'`，旧规则只写到 `'</p>'`
  - 修复记忆栏说明句半截汉化（"记忆 are durable facts…"）
  - 补齐 `Shown: N total.`、`— click to expand`、`↻ Rebuild Graph`、`Engine connection lost — reconnecting.`、
    `% of allocated heap in use …`、`Requires an LLM provider key …` 等长句的后半段
  - 枚举值汉化扩展到断路器 / 工作进程 / 会话 / 操作状态与回放事件类型（新增 `VAL_ZH` 项 29 个）
  - 新增注入后 JS 语法自检与 `valZh` 断言脚本

## 校验脚本（可选）

`apply` 之后建议跑一次，确认替换没有破坏内联 JS（需要 Node.js）：

```bash
# 1) 内联 <script> 语法自检（只解析，不执行）
node tools/check_js_syntax.js "C:\path\to\...\dist\viewer\index.html"

# 2) valZh 枚举映射断言 + 渲染点切换检查（含 CSS 类未被误改）
node tools/verify_valzh.js "C:\path\to\...\dist\viewer\index.html"
```

两者通过时打印 `[OK]` 并以退出码 0 结束，可直接接入 CI。

## 安装前提

- 已安装并运行 [agentmemory](https://github.com/rohitg00/agentmemory)（`npx @agentmemory/agentmemory`）
- Python 3.8+（无第三方依赖，纯标准库）

## License

MIT。上游 [agentmemory](https://github.com/rohitg00/agentmemory) 为 Apache-2.0，本补丁仅修改本地已安装的文件，不重分发上游代码。

---

*Made with 🛢️ by [yaheng100](https://github.com/yaheng100)*
