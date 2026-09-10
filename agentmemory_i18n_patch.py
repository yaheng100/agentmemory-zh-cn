#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agentmemory Viewer 汉化补丁 (agentmemory-viewer-chinese-patch)
================================================================
为 agentmemory (https://github.com/rohitg00/agentmemory) 的内置
Viewer (:3113) 提供简体中文界面。纯文案替换，不改任何功能逻辑。

用法:
    python agentmemory_i18n_patch.py apply    # 应用汉化（自动备份原文）
    python agentmemory_i18n_patch.py restore  # 恢复官方英文原文
    python agentmemory_i18n_patch.py check    # 检测兼容性（不改文件）
    python agentmemory_i18n_patch.py apply --file <index.html 路径>  # 手动指定

适配版本: agentmemory v0.9.29（其他版本可用 check 检测命中率）
许可: MIT（上游 agentmemory 为 Apache-2.0）
"""
import argparse
import os
import shutil
import subprocess
import sys

# ------------------------------------------------------------------
# 1. 静态文本节点:  ">English<"  ->  ">中文<"
# ------------------------------------------------------------------
I18N_TEXT = {
    # 标题与导航
    "agentmemory viewer": "agentmemory 记忆查看器",
    "Sessions": "会话", "Memories": "记忆", "Lessons": "经验", "Graph": "图谱",
    "Crystals": "晶体", "Actions": "操作", "Replay": "回放", "Health": "健康",
    "Profile": "画像", "Workers": "工作进程", "Timeline": "时间线",
    "Dashboard": "仪表盘", "Audit": "审计", "Conventions": "约定",
    "Activity": "活动", "Files": "文件",
    # 仪表盘
    "Recent Activity": "最近动态", "Recent Sessions": "最近会话",
    "Project Stats": "项目统计", "Project Summary": "项目摘要",
    "Type Breakdown": "类型分布", "Top Concepts": "高频概念", "Top Files": "高频文件",
    "Token Savings": "Token 节省", "Tool Invocations": "工具调用",
    "Total Obs": "观测总数", "System Resources": "系统资源",
    "OBSERVATIONS": "观测记录", "LESSONS SURFACED": "浮现的经验",
    "TOOLS USED": "使用过的工具", "FILES TOUCHED": "触及的文件",
    "Activity Breakdown": "动态分布", "Activity Feed": "动态流",
    "Activity Heatmap (Past Year)": "活跃度热力图（过去一年）",
    "All importance": "全部重要度", "All operations": "全部操作",
    "All statuses": "全部状态", "Auto-refresh 30s": "自动刷新 30s",
    "Avg Latency": "平均延迟", "Circuit Breaker": "熔断器",
    "Circuit Breaker Details": "熔断器详情", "Consolidation Status": "整合状态",
    "DURATION": "耗时", "Event Loop": "事件循环", "Feature flags": "功能开关",
    "live updates off": "实时更新已关闭", "auto-import": "自动导入",
    "raw record": "原始记录", "decisions to revisit": "待重审的决策",
    "tasks blocked on input": "等待输入的任务", "files to inspect": "待检查的文件",
    "action digests": "操作摘要", "confidence-scored": "置信度评分",
    "frontier": "前沿", "latest versions": "最新版本", "docs": "文档",
    # 图谱
    "Memory Relations": "记忆关系", "Graph Nodes": "图谱节点", "Graph Stats": "图谱统计",
    "Knowledge graph is off": "知识图谱未开启", "Graph query failed": "图谱查询失败",
    "Rebuilding graph from observations...": "正在从观测重建图谱...",
    "Legend": "图例", "Relations": "关系", "Nodes": "节点",
    "Filter by Type": "按类型筛选", "Expand neighbors": "展开邻居",
    "Edges": "边",
    # 会话详情
    "Select a session to view observations": "选择一个会话以查看观测",
    "Select session": "选择会话", "Import JSONL": "导入 JSONL",
    "Started": "开始时间", "Opened At": "打开时间", "Updated": "更新时间",
    "Last Failure": "最近失败", "Input": "输入", "Output": "输出",
    "Title": "标题", "Type": "类型", "Status": "状态", "State": "状态",
    "Source": "来源", "Tags": "标签", "Metadata": "元数据", "Version": "版本",
    "Priority": "优先级", "Quality": "质量", "Strength": "强度",
    "Uses": "使用次数", "Why learned": "学因", "Success": "成功",
    "Procedural Memory": "程序性记忆", "Semantic Memory": "语义记忆",
    "Semantic facts": "语义事实", "Procedures": "流程", "Lesson": "经验",
    "Obs": "观测", "Next": "下一个", "Prev": "上一个",
    "Confidence": "置信度", "Failures": "失败次数", "Fail": "失败",
    # 函数/系统
    "Function Calls": "函数调用", "Function Metrics (OTel)": "函数指标 (OTel)",
    "Heap": "堆内存", "RSS": "常驻内存",
    # 按钮
    "Refresh": "刷新", "Delete": "删除", "Retry": "重试", "Unlock": "解锁",
    "Cancel": "取消", "Calls": "调用",
    # 加载提示
    "Loading actions...": "加载操作...", "Loading activity...": "加载动态...",
    "Loading audit log...": "加载审计日志...", "Loading crystals...": "加载晶体...",
    "Loading dashboard...": "加载仪表盘...", "Loading lessons...": "加载经验...",
    "Loading memories...": "加载记忆...", "Loading observations...": "加载观测...",
    "Loading profile data...": "加载画像数据...", "Loading profile...": "加载画像...",
    "Loading sessions...": "加载会话...", "Loading timeline...": "加载时间线...",
    "loading...": "加载中...",
    # 空状态
    "No actions tracked yet": "暂无操作记录", "No activity recorded yet": "暂无动态",
    "No audit entries yet": "暂无审计记录", "No conventions detected yet": "未检测到约定",
    "No crystals yet": "暂无晶体", "No event selected.": "未选择事件。",
    "No files yet": "暂无文件", "No lessons yet": "暂无经验",
    "No memories yet": "暂无记忆", "No observations yet": "暂无观测",
    "No profile data for this project": "该项目暂无画像数据",
    "No projects": "暂无项目", "No recent activity": "暂无最近动态",
    "No sessions": "暂无会话",
    # 授权
    "Viewer authorization required": "查看器需要授权",
    # ---- 第二轮补漏（2026-09-10）：带冒号/独立词的文本节点 ----
    # 说明：形如 ">Input:<" 的节点，旧的 "Input" 规则因带冒号而无法命中，故单列
    "Frontier": "前沿", "External": "外部",
    "End Session": "结束会话",
    "Summarize unavailable": "无法生成摘要", "Summarize": "生成摘要",
    "Input:": "输入：", "Output:": "输出：", "Tool:": "工具：",
    "cwd:": "工作目录：", "started:": "开始：", "ended:": "结束：",
    "model:": "模型：", "tags:": "标签：", "id:": "ID：",
}

# ------------------------------------------------------------------
# 2. title / placeholder 属性
# ------------------------------------------------------------------
I18N_ATTRS = {
    "Zoom In": "放大", "Zoom Out": "缩小", "Recenter": "复位", "Reset": "重置",
    "Play/Pause (Space)": "播放/暂停 (空格)",
    "How battle-tested the rule is. Grows each time it is reinforced, decays weekly when unused.":
        "该规则的实战验证程度。每次被强化时增长，闲置每周衰减。",
    "Times the agent re-confirmed this rule.": "Agent 重新确认此规则的次数。",
}
I18N_PLACEHOLDERS = {
    "Search actions...": "搜索操作...", "Search crystals...": "搜索晶体...",
    "Search lessons...": "搜索经验...", "Search memories...": "搜索记忆...",
    "Search nodes...": "搜索节点...",
}

# ------------------------------------------------------------------
# 3. JS 字符串精确替换（引号锚定，避免误伤代码）
#    覆盖: 动态拼接文案 / 状态消息 / 空状态长段落 / 对话框 / 按钮文案
# ------------------------------------------------------------------
I18N_JS = [
    # 空状态长说明（各 Tab 的 empty-lead）
    ("Actions are follow-ups the agent surfaced during a session: ",
     "操作是 agent 在会话中提出的后续事项："),
    ("Crystals are frozen snapshots of completed work &mdash; one session\u2019s narrative, key outcomes, files touched, and lessons surfaced, kept after raw observations are pruned so the next session gets fast context.",
     "晶体是已完成工作的冻结快照 &mdash; 包含该会话的完整叙事、关键产出、触及文件与浮现的经验。在原始观测被修剪后仍然保留，让下一个会话快速获得上下文。"),
    ("Lessons are short imperative rules (always/never/prefer/avoid) learned from past work &mdash; things you corrected once that the agent should never repeat. Confidence grows when they hold and decays when unused.",
     "经验是从过往工作中提炼的短命令式规则（总是/绝不/优先/避免）&mdash; 即你纠正过一次、agent 就不该再犯的事。规则持续生效时置信度增长，闲置则衰减。"),
    ("Memories are the distilled facts agentmemory keeps across sessions &mdash; things like file paths, architectural decisions, and user preferences. Hooks capture them automatically during coding sessions; you can also save one directly.",
     "记忆是 agentmemory 跨会话保留的提炼事实 &mdash; 例如文件路径、架构决策、用户偏好。编码会话中由 hooks 自动捕获，也可以手动保存。"),
    ("s narrative, the tools invoked (key outcomes), files touched, and lessons surfaced \u2014 a replayable summary you keep after raw observations are pruned. Auto-created on JSONL import or via <code>memory_crystallize</code>.",
     "的完整叙事、调用的工具（关键产出）、触及文件与浮现的经验 \u2014 原始观测被修剪后仍保留的可回放摘要。在 JSONL 导入或通过 <code>memory_crystallize</code> 时自动创建。"),
    ("Consolidation distills session observations into durable facts and repeatable procedures. It runs on a schedule when <code>CONSOLIDATION_ENABLED=true</code> and an LLM provider key are set, or on demand via <code>memory_consolidate</code>.",
     "整合（Consolidation）会把会话观测蒸馏为持久事实与可复用流程。当设置了 <code>CONSOLIDATION_ENABLED=true</code> 和 LLM provider 密钥时按计划自动运行，也可通过 <code>memory_consolidate</code> 按需触发。"),
    ("No semantic facts yet. Observations will be consolidated into semantic memories over time.",
     "暂无语义事实。观测会随时间被整合为语义记忆。"),
    ("No concepts yet. Concepts are tagged when observations are compressed by an LLM (<code>AGENTMEMORY_AUTO_COMPRESS=true</code> + provider key) or attached to saved memories.",
     "暂无概念。当观测被 LLM 压缩（<code>AGENTMEMORY_AUTO_COMPRESS=true</code> + provider 密钥）或关联到已保存记忆时，会打上概念标签。"),
    ("agentmemory is running but hasn&rsquo;t seen any sessions yet. Run the demo command in a second terminal: it seeds 3 realistic coding sessions and proves the hybrid search finds semantically-related memories that keyword search would miss.",
     "agentmemory 正在运行但还没有任何会话。在另一个终端运行 demo 命令：它会注入 3 个真实感编码会话，并演示混合搜索如何找到关键词搜索找不到的语义相关记忆。"),
    ("No sessions yet. Start a coding session with agentmemory hooks enabled.",
     "暂无会话。开启 agentmemory hooks 后开始一次编码会话即可。"),
    # 删除确认对话框
    ('<h3>Delete Memory</h3><p>Are you sure you want to delete "',
     '<h3>删除记忆</h3><p>确定要删除 "'),
    ('"? This action cannot be undone.', '"？此操作不可撤销。'),
    # 观测筛选动态拼接（旧键开头多写了一个单引号，实际源码里 'No observations'
    # 前面是 '>'（<p>No observations'），故从未命中；后文第二轮补漏里已按 '>No observations' 重写）
    ("' observations shown</div>'", "' 条观测已显示</div>'"),
    # 状态与提示消息
    ("'Running in BM25-only mode'", "'正以纯 BM25 模式运行'"),
    ("'No LLM provider key set'", "'未设置 LLM provider 密钥'"),
    ("Compression, summarization, and graph extraction stay disabled until a key is provided.",
     "在提供密钥之前，压缩、摘要与图谱抽取保持关闭。"),
    ("Semantic vector search is off. BM25 keyword search is active and good for exact matches.",
     "语义向量搜索已关闭。BM25 关键词搜索已生效，适合精确匹配。"),
    ("Set GRAPH_EXTRACTION_ENABLED=true to enable knowledge graph extraction.",
     "设置 GRAPH_EXTRACTION_ENABLED=true 可开启知识图谱抽取。"),
    ("Check the browser console for the full error. If you see CSP ",
     "完整错误请查看浏览器控制台。如果看到 CSP "),
    ("violations, please open an issue with the agentmemory version ",
     "违规，请携带 agentmemory 版本号提交 issue："),
    # humanizeHealthFlag：整条 return 语句替换。
    # 早前版本把 "'critically high'"、"n'Event loop '" 等拆成单词替换，
    # 既容易漏翻后半句（"% of allocated heap in use ..."），又会因列表先后顺序
    # 互相破坏。这里按整句替换，一次到位。
    ("return 'Heap is running tight: ' + m[1] + '% of allocated heap in use "
     "(process memory ' + m[2] + ' MB). Informational \u2014 Node grows the heap on demand.';",
     "return '堆内存吃紧：' + m[1] + '% 已分配堆在使用中（进程内存 ' + m[2] "
     "+ ' MB）。仅供参考 \u2014\u2014 Node 会按需增长堆。';"),
    ("return 'Memory ' + (m[1] === 'critical' ? 'critically high' : 'elevated') + "
     "': ' + m[2] + '% of heap in use, process memory ' + m[3] + ' MB.';",
     "return '内存' + (m[1] === 'critical' ? '严重偏高' : '偏高') + '：' + m[2] "
     "+ '% 堆在使用中，进程内存 ' + m[3] + ' MB。';"),
    ("return 'CPU ' + (m[1] === 'critical' ? 'critically high' : 'elevated') + "
     "': ' + m[2] + '%.';",
     "return 'CPU ' + (m[1] === 'critical' ? '严重偏高' : '偏高') + '：' + m[2] + '%。';"),
    ("return 'Event loop ' + (m[1] === 'critical' ? 'severely delayed' : 'delayed') + "
     "': ' + m[2] + ' ms behind. The worker is busy or blocked.';",
     "return '事件循环' + (m[1] === 'critical' ? '严重延迟' : '延迟') + '：落后 ' + m[2] "
     "+ ' ms。工作线程繁忙或被阻塞。';"),
    ("return 'Engine connection lost \u2014 reconnecting.';",
     "return '引擎连接已断开 \u2014\u2014 正在重连。';"),
    ("return 'Engine connection state: ' + m[1] + '.';",
     "return '引擎连接状态：' + m[1] + '。';"),
    ("'No graph data yet.'", "'暂无图谱数据。'"),
    ("No graph data yet. Building from observations and memories...",
     "暂无图谱数据。正在从观测和记忆构建..."),
    ("'Unknown session'", "'未知会话'"),
    ("'Untitled crystal'", "'未命名晶体'"),
    ("'Import failed'", "'导入失败'"),
    ("'Deleted via viewer'", "'通过查看器删除'"),
    ("'Dashboard failed to load: '", "'仪表盘加载失败：'"),
    # 已删除的死键（均从未命中，保留只会误导）：
    #   "'query failed / Retry'" / "'request failed'" / "'no data yet'" / "'Rebuild Graph'"
    #     —— 原文里只出现在 // 注释中且用双引号，非用户可见
    #   "'Open dashboard'"  —— 原文是 aria-label="Open dashboard"，已由属性规则处理
    #   "'Shown: '"          —— 原文是 >Shown: ，已由 ">Shown: " 规则处理
    #   "'End Session'"      —— 原文是 >End Session</button>，已由 I18N_TEXT 处理

    ("'Imported '", "'已导入 '"),
    ("'Done'", "'完成'"),
    # Showing 拼接整句替换（只换 'Showing ' 会留下 "N of M nodes (most-connected first)..." 半截英文）
    ("'Showing ' + state.graph.nodes.length + ' of ' + state.graph.totalNodes + "
     "' nodes (most-connected first). The full graph is too large to render at once.';",
     "'显示前 ' + state.graph.nodes.length + ' / ' + state.graph.totalNodes + "
     "' 个节点（按连接数降序）。完整图谱过大，无法一次性渲染。';"),
    # 注意：这几条在原文里是 <h3>…</h3> / >…</div> 形态（Unicode 省略号 U+2026），
    # 前面不是单引号。旧版误写成 "'Loading replay…'" 带引号锚点，故从未命中。
    ("<h3>Loading session details\u2026</h3>", "<h3>加载会话详情\u2026</h3>"),
    (">Importing JSONL\u2026</div>", ">导入 JSONL\u2026</div>"),
    ("Alerts (", "告警 ("),
    ("Notes (", "备注 ("),
    ("Pick a session to replay, or import Claude Code JSONL transcripts from ~/.claude/projects.",
     "选择一个会话进行回放，或从 ~/.claude/projects 导入 Claude Code 的 JSONL 转录。"),
    (">Loading replay\u2026</div>", ">加载回放\u2026</div>"),
    (">Loading sessions\u2026</div>", ">加载会话\u2026</div>"),
    # 动态按钮文案
    ("btn.textContent = 'Summarize'", "btn.textContent = '生成摘要'"),
    ("btn.textContent = 'Summarizing", "btn.textContent = '摘要生成中"),
    # 主题切换
    ("'DARK'", "'深色'"), ("'LIGHT'", "'浅色'"),
    ("'End Session'", "'结束会话'"),

    # ---- 第二轮补漏（2026-09-10）----
    # 记忆栏说明句：原文 <strong>Memories</strong> 被文本节点规则单独翻成"记忆"，
    # 导致出现"记忆 are durable facts..."半截汉化。此处把英文后半句整体替换。
    ("are durable facts, architecture notes, conventions, and lessons saved via "
     "<code>memory_remember</code> MCP tool or the <code>/agentmemory/remember</code> "
     "endpoint. They survive across sessions and supersede each other as v1, v2, etc. ",
     "是持久的事实、架构笔记、约定与经验，通过 <code>memory_remember</code> MCP 工具或 "
     "<code>/agentmemory/remember</code> 接口保存。它们跨会话保留，并以 v1、v2 等版本互相取代。"),
    # 计数文案：旧规则 "'Shown: '" 多了引号，从未命中；"total." 同样漏掉
    (">Shown: ", ">已显示 "),
    (" total.</span>", " 条</span>"),
    # 观测筛选结果三元表达式整体替换（'No observations' 的 yet 分支已由文本规则处理）
    # 注意：源码结尾是 '</p></div>'，旧版只写到 '</p>'，故从未命中。
    (">No observations' + (obs.length > 0 ? ' match the filter (' + obs.length + ' total)' "
     ": ' for this session') + '</p></div>'",
     ">暂无观测' + (obs.length > 0 ? ' 条匹配筛选（共 ' + obs.length + ' 条）' "
     ": ' 属于本次会话') + '</p></div>'"),
    # 功能开关折叠提示："— click to " + collapse/expand
    (">\u2014 click to ", ">\u2014 点击"),
    ("'collapse' : 'expand'", "'收起' : '展开'"),
    # 记忆详情/会话详情/经验/审计 的字段标签（形如 ">id: "，带空格故文本规则不命中）
    (">id: ", ">ID："), (">origin: ", ">来源："), (">project: ", ">项目："),
    (">created: ", ">创建："), (">supersedes: ", ">取代："), (">files: ", ">文件："),
    (">tags: ", ">标签："), (">learned: ", ">学到："), (">last confirmed: ", ">最近确认："),
    (">from ", ">来自 "),
    # 各栏空状态说明与文档链接
    ("report issue &rarr;", "反馈问题 &rarr;"),
    ("Seed sample data", "填充示例数据"),
    ("Or: wire up your real agent &rarr;", "或：接入你自己的 agent &rarr;"),
    ("First run &rarr;", "首次运行 &rarr;"),
    ("No procedures yet. Repeated patterns will be extracted as procedures.",
     "暂无程序性记忆。重复出现的模式会被抽取为流程。"),
    (">Trigger: ", ">触发："), (">Freq: ", ">频次："),
    (">docs &rarr;", ">文档 &rarr;"),
    ("Entities extracted, no relations between them yet. Nodes are grouped by kind; "
     "edges appear as extraction sees entities acting on each other across more sessions "
     "(larger models find them faster).",
     "已抽取实体，但暂未发现实体间的关系。节点按类型分组；当抽取发现实体在更多会话中互相作用时，"
     "就会出现边（模型越大发现越快）。"),
    (">Connections: ", ">连接数："),
    ("Memory types &rarr;", "记忆类型 &rarr;"),
    ("Three ways to create them:", "三种创建方式："),
    ("Action lifecycle docs &rarr;", "操作生命周期文档 &rarr;"),
    ("Crystal pipeline &rarr;", "晶体流水线 &rarr;"),
    ("Audit entries are created by governance operations (delete, evolve, consolidate).",
     "审计记录由治理操作产生（删除、演进、整合）。"),
    ("Learn more &rarr;", "了解更多 &rarr;"),
    ("Lesson decay &amp; scoring &rarr;", "经验衰减与评分 &rarr;"),

    # ---- 第三轮补漏（2026-09-10）----
    # 1) 图谱区按钮与错误态
    (">\u21bb Rebuild Graph</button>", ">\u21bb 重建图谱</button>"),
    ("= 'graph/query failed (check server logs for HTTP error)';",
     "= '图谱查询失败（请检查服务端日志中的 HTTP 错误）';"),
    # 2) 功能开关横幅：需要 LLM key 的提示
    ("' Requires an LLM provider key (ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.).'",
     "' 需要设置 LLM provider 密钥（ANTHROPIC_API_KEY、GEMINI_API_KEY 等）。'"),
    # 3) 知识图谱关闭时的启用指引 "Set <FLAG>=true and restart."
    ("'Set ' + (state.graph.disabledInfo.flag || 'GRAPH_EXTRACTION_ENABLED') "
     "+ '=true and restart.'",
     "'设置 ' + (state.graph.disabledInfo.flag || 'GRAPH_EXTRACTION_ENABLED') "
     "+ '=true 并重启。'"),
    # 4) 仪表盘错误提示结尾
    ("'(top-right of the viewer) and the violation text.'",
     "'（位于查看器右上角）以及违规文本。'"),
    # 5) 可访问性标签 / 属性
    ('aria-label="Open dashboard"', 'aria-label="打开仪表盘"'),
    ('aria-label="Dismiss"', 'aria-label="关闭"'),
    ('title="Importance: ', 'title="重要度：'),
    ('title="Next (\u2192)"', 'title="下一个 (\u2192)"'),
    ('title="Previous (\u2190)"', 'title="上一个 (\u2190)"'),
    ('placeholder="~/.claude/projects or file.jsonl"',
     'placeholder="~/.claude/projects 或 file.jsonl"'),

    # ---- 第三轮补漏（2026-09-10）：状态类枚举值显示汉化 ----
    # 断路器 / 工作进程 / 会话 / 操作 / 回放事件 kind，与 VAL_ZH 同一机制：
    # 只换显示文本，筛选参数与入库原值保持英文。
    ("esc(cb.state) + '</span>", "valZh(cb.state) + '</span>"),
    ("esc(w.status) + '</span>", "valZh(w.status) + '</span>"),
    ("esc(s.status) + '</span>", "valZh(s.status) + '</span>"),
    ("esc(a.status) + '</span>", "valZh(a.status) + '</span>"),
    ("esc(ev.kind) + '</span>", "valZh(ev.kind) + '</span>"),
    # 仪表盘健康卡片：健康状态 + 连接状态（截图实测 healthy / connected 直出英文）
    ("esc(healthStatus) + '</div>", "valZh(healthStatus) + '</div>"),
    ("esc(snap.connectionState || 'unknown')", "valZh(snap.connectionState || 'unknown')"),
    ("' failures</div></div>'", "' 次失败</div></div>'"),
    ("+ '>' + s + '</option>'", "+ '>' + valZh(s) + '</option>'"),

    # ---- 第四轮补漏（2026-09-10，headless 浏览器逐 tab 渲染实测发现）----
    # 静态扫描看不到这些：要么由 JS 在运行时拼出，要么藏在代码块的注释里。
    # 1) 头部日期：原文 new Date().toLocaleDateString('en-US', …) 渲染出 "Thu, Sep 10, 2026"
    ("toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', "
     "month: 'short', day: 'numeric' })",
     "toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', "
     "day: 'numeric', weekday: 'long' })"),
    # 2) 右上角 WebSocket 状态标签（live / connecting... / polling · Ns）
    ("setWsStatus('live', 'connected')", "setWsStatus('实时', 'connected')"),
    ("setWsStatus('connecting...', 'disconnected')",
     "setWsStatus('连接中...', 'disconnected')"),
    ("setWsStatus('polling · ' + (POLL_INTERVAL_MS / 1000) + 's', 'disconnected')",
     "setWsStatus('轮询 · 每 ' + (POLL_INTERVAL_MS / 1000) + ' 秒', 'disconnected')"),
    # 3) 审计栏的目标数量
    ("+ ' target(s): '", "+ ' 个目标：'"),
    # 3b) 活动栏的目标数量（另一种拼接形态，截图实测 "[25 targets]"）
    ("+ ' targets)</span>'", "+ ' 个目标)</span>'"),
    # 3c) Token 节省卡片尾部（截图实测 "~2,376,160 tokens · $712.85 saved"）
    ("+ ' tokens · '", "+ ' 个 token · 节省 '"),
    ("+ ' saved</div></div>'", "+ '</div></div>'"),
    # 3d) 仪表盘统计卡副标题（截图实测 "0 active" / "E357 edges" / "0 functions tracked"）
    ("+ ' active</div></div>'", "+ ' 个进行中</div></div>'"),
    ("+ ' edges</div></div>'", "+ ' 条边</div></div>'"),
    ("+ ' functions tracked</div></div>'", "+ ' 个函数</div></div>'"),
    # 4) 空状态「怎么创建」代码块里的英文注释（命令本体保持原样，只翻说明）
    ("# Save a lesson explicitly\\nmemory_lesson_save",
     "# 显式保存一条经验\\nmemory_lesson_save"),
    ("# Or: Replay tab &rarr; Import JSONL auto-extracts lessons\\n"
     "# from your past Claude Code sessions",
     "# 或者：回放页签 &rarr; 导入 JSONL 会自动抽取经验\\n"
     "# 来源：你过往的 Claude Code 会话"),
    ("# 1. MCP tool (from any agent)", "# 1. MCP 工具（任意 agent 均可调用）"),
    ("# 2. Curl", "# 2. Curl 命令"),
    ("# 3. Hooks auto-extract from long session bodies",
     "# 3. Hooks 会从长会话正文自动抽取"),
    ("# Auto: import a JSONL transcript\\n#   Replay tab &rarr; Import JSONL\\n\\n"
     "# Manual: crystallize a specific session",
     "# 自动：导入一段 JSONL 转录\\n#   回放页签 &rarr; 导入 JSONL\\n\\n"
     "# 手动：对指定会话做结晶"),
]

# 表格表头 / 控件（HTML 结构形态）
I18N_STRUCT = [
    ("<th>Project</th>", "<th>项目</th>"),
    ("<th>Function</th>", "<th>函数</th>"),
    ('<option value="">All types</option>', '<option value="">全部类型</option>'),
    (">Enter <code>", ">输入 <code>"),
    (">DARK<", ">深色<"),
    (">Speed<", ">速度<"),

    # ---- 第二轮补漏（2026-09-10）：枚举值显示汉化 ----
    # 记忆类型 / 审计操作 / 关系类型 / 断路器状态 / 工作进程状态 / 会话状态 /
    # 操作状态 / 回放事件 kind 的"显示值"汉化。
    # 只改显示文本，<option value="...">、筛选参数、入库数据一律保持英文原值，不影响逻辑。
    # 做法：在 TYPE_BADGES 定义之后注入 VAL_ZH 映射表 + valZh() 函数，
    #       再把各渲染点由 esc(x) 换成 valZh(x)。
    ("      bug: 'badge-red', workflow: 'badge-green', fact: 'badge-yellow'\n    };",
     "      bug: 'badge-red', workflow: 'badge-green', fact: 'badge-yellow'\n    };\n"
     "    var VAL_ZH = {\n"
     "      pattern: '\u6a21\u5f0f', preference: '\u504f\u597d', architecture: '\u67b6\u6784',\n"
     "      bug: '\u7f3a\u9677', workflow: '\u6d41\u7a0b', fact: '\u4e8b\u5b9e',\n"
     "      observe: '\u89c2\u5bdf', compress: '\u538b\u7f29', remember: '\u8bb0\u4f4f', forget: '\u9057\u5fd8',\n"
     "      evolve: '\u6f14\u8fdb', consolidate: '\u6574\u5408', share: '\u5171\u4eab', delete: '\u5220\u9664',\n"
     "      import: '\u5bfc\u5165', export: '\u5bfc\u51fa',\n"
     "      supersedes: '\u53d6\u4ee3', extends: '\u6269\u5c55', contradicts: '\u51b2\u7a81', related: '\u76f8\u5173',\n"
     "      closed: '\u5df2\u5173\u95ed', open: '\u5df2\u65ad\u5f00', 'half-open': '\u534a\u5f00',\n"
     "      running: '\u8fd0\u884c\u4e2d', starting: '\u542f\u52a8\u4e2d', stopped: '\u5df2\u505c\u6b62',\n"
     "      active: '\u8fdb\u884c\u4e2d', completed: '\u5df2\u5b8c\u6210', done: '\u5df2\u5b8c\u6210',\n"
     "      pending: '\u5f85\u5904\u7406', blocked: '\u53d7\u963b', cancelled: '\u5df2\u53d6\u6d88',\n"
     "      prompt: '\u63d0\u793a\u8bcd', response: '\u54cd\u5e94',\n"
     "      tool_call: '\u5de5\u5177\u8c03\u7528', tool_error: '\u5de5\u5177\u9519\u8bef',\n"
     "      tool_result: '\u5de5\u5177\u7ed3\u679c',\n"
     "      healthy: '\u5065\u5eb7', degraded: '\u964d\u7ea7', critical: '\u4e25\u91cd', unknown: '\u672a\u77e5',\n"
     "      connected: '\u5df2\u8fde\u63a5', disconnected: '\u672a\u8fde\u63a5'\n"
     "    };\n"
     "    function valZh(v) {\n"
     "      var k = String(v == null ? '' : v).toLowerCase();\n"
     "      return VAL_ZH[k] || v;\n"
     "    }"),
    ("esc(m.type) + '</span></td>'", "valZh(m.type) + '</span></td>'"),
    ("' + esc(t) + '</option>'", "' + valZh(t) + '</option>'"),
    ("esc(a.operation) + '</span> '", "valZh(a.operation) + '</span> '"),
    ("esc(relType) + '</span>'", "valZh(relType) + '</span>'"),
]

BACKUP_SUFFIX = ".bak-en"
MARKER = 'lang="zh-CN"'


def find_viewer_html(explicit):
    """定位 viewer 的 index.html"""
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        print(f"[!] 指定路径不存在: {explicit}")
        sys.exit(1)
    # 0) 环境变量兜底
    env_path = os.environ.get("AGENTMEMORY_VIEWER_HTML", "")
    if env_path and os.path.isfile(env_path):
        return env_path
    # 1) npm 全局根目录
    try:
        r = subprocess.run(["npm", "root", "-g"], capture_output=True,
                           text=True, timeout=30, shell=(os.name == "nt"))
        root = (r.stdout or "").strip()
        if root:
            cand = os.path.join(root, "@agentmemory", "agentmemory",
                                "dist", "viewer", "index.html")
            if os.path.isfile(cand):
                return cand
    except Exception:
        pass
    # 2) 通过 agentmemory 命令位置反推（兼容 npm --prefix 自定义安装）
    try:
        which = "where" if os.name == "nt" else "which"
        r = subprocess.run([which, "agentmemory"], capture_output=True,
                           text=True, timeout=30, shell=(os.name == "nt"))
        for line in (r.stdout or "").splitlines():
            line = line.strip()
            if not line:
                continue
            base = os.path.dirname(os.path.abspath(line))
            cand = os.path.join(base, "node_modules", "@agentmemory",
                                "agentmemory", "dist", "viewer", "index.html")
            if os.path.isfile(cand):
                return cand
            # npm 全局 prefix 布局: <prefix>/node_modules/@agentmemory/...
            cand2 = os.path.join(os.path.dirname(base), "node_modules",
                                 "@agentmemory", "agentmemory",
                                 "dist", "viewer", "index.html")
            if os.path.isfile(cand2):
                return cand2
    except Exception:
        pass
    # 3) 常见安装位置
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "AppData", "Roaming", "npm", "node_modules",
                     "@agentmemory", "agentmemory", "dist", "viewer", "index.html"),
        os.path.join(home, ".local", "share", "npm", "node_modules",
                     "@agentmemory", "agentmemory", "dist", "viewer", "index.html"),
        "/usr/local/lib/node_modules/@agentmemory/agentmemory/dist/viewer/index.html",
        "/usr/lib/node_modules/@agentmemory/agentmemory/dist/viewer/index.html",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def count_hits(s):
    """统计当前文件能命中多少条翻译（用于 check）"""
    hits = 0
    for en in I18N_TEXT:
        if ">" + en + "<" in s:
            hits += 1
    for en in I18N_ATTRS:
        if 'title="' + en + '"' in s:
            hits += 1
    for en in I18N_PLACEHOLDERS:
        if 'placeholder="' + en + '"' in s:
            hits += 1
    for old, _ in I18N_JS:
        if old in s:
            hits += 1
    for old, _ in I18N_STRUCT:
        if old in s:
            hits += 1
    return hits


def do_apply(path):
    with open(path, encoding="utf-8") as f:
        s = f.read()

    if MARKER in s:
        print("[=] 该文件已汉化过，跳过重复应用。")
        print("    如需重打（例如刚升级了 agentmemory），先运行: python agentmemory_i18n_patch.py restore")
        return

    backup = path + BACKUP_SUFFIX
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
        print(f"[+] 已备份原文 -> {backup}")
    else:
        print(f"[i] 备份已存在，保留最初英文原文: {backup}")

    n_text = n_attr = n_js = n_struct = 0
    for en in sorted(I18N_TEXT, key=len, reverse=True):
        if ">" + en + "<" in s:
            s = s.replace(">" + en + "<", ">" + I18N_TEXT[en] + "<")
            n_text += 1
    for en in I18N_ATTRS:
        if 'title="' + en + '"' in s:
            s = s.replace('title="' + en + '"', 'title="' + I18N_ATTRS[en] + '"')
            n_attr += 1
    for en in I18N_PLACEHOLDERS:
        if 'placeholder="' + en + '"' in s:
            s = s.replace('placeholder="' + en + '"',
                          'placeholder="' + I18N_PLACEHOLDERS[en] + '"')
            n_attr += 1
    for old, new in I18N_JS:
        if old in s:
            s = s.replace(old, new)
            n_js += 1
    for old, new in I18N_STRUCT:
        if old in s:
            s = s.replace(old, new)
            n_struct += 1

    s = s.replace('<html lang="en">', '<html lang="zh-CN">')
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)

    total = n_text + n_attr + n_js + n_struct
    print(f"[OK] 汉化完成: 静态文本 {n_text} | 属性 {n_attr} | JS 动态 {n_js} | 结构 {n_struct} | 共 {total}")
    if total < 100:
        print("[!] 命中率偏低，可能 agentmemory 版本不兼容，"
              "请到补丁仓库查看版本适配说明。")
    print("[i] 浏览器强制刷新 (Ctrl+F5) 即可看到中文界面，无需重启服务。")


def do_restore(path):
    backup = path + BACKUP_SUFFIX
    if os.path.exists(backup):
        shutil.copy2(backup, path)
        print(f"[OK] 已恢复官方英文原文: {path}")
    elif MARKER in open(path, encoding="utf-8").read():
        print("[!] 没找到备份文件，但文件已汉化。请重装 agentmemory 或手动处理。")
        sys.exit(1)
    else:
        print("[i] 文件本来就是英文原文，无需恢复。")


def main():
    ap = argparse.ArgumentParser(
        description="agentmemory Viewer 汉化补丁 (v1.0.0, 适配 agentmemory 0.9.29)")
    ap.add_argument("action", choices=["apply", "restore", "check"],
                    help="apply=应用汉化 / restore=恢复英文 / check=检测兼容性")
    ap.add_argument("--file", help="手动指定 viewer index.html 路径（默认自动定位）")
    args = ap.parse_args()

    path = find_viewer_html(args.file)
    if not path:
        print("[!] 未找到 viewer index.html。请确认已安装 agentmemory，")
        print("    或用 --file 手动指定路径。")
        sys.exit(1)
    print(f"[i] 目标文件: {path}")

    with open(path, encoding="utf-8") as f:
        s = f.read()

    if args.action == "check":
        hits = count_hits(s)
        if MARKER in s:
            print(f"[=] 当前已汉化（check 命中 {hits} 条仅为参考）。")
        elif hits >= 100:
            print(f"[OK] 版本兼容，可命中 {hits} 条翻译，放心 apply。")
        elif hits > 0:
            print(f"[!] 部分兼容（仅命中 {hits} 条），可能版本不同，"
                  f"apply 后会有残留英文。")
        else:
            print("[X] 完全不兼容（0 命中），viewer 结构可能已大改。")
        sys.exit(0)

    if args.action == "apply":
        do_apply(path)
    elif args.action == "restore":
        do_restore(path)


if __name__ == "__main__":
    main()
