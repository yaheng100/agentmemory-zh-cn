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
    # 观测筛选动态拼接
    ("'No observations' + (obs.length > 0 ? ' match the filter (' + obs.length + ' total)' : ' for this session') + '",
     "'暂无观测' + (obs.length > 0 ? '匹配当前筛选（共 ' + obs.length + ' 条）' : '——本会话') + '"),
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
    ("'critically high'", "'严重偏高'"),
    ("'severely delayed'", "'严重延迟'"),
    ("'Heap is running tight: '", "'堆内存吃紧：'"),
    ("'Event loop '", "'事件循环 '"),
    ("'Engine connection state: '", "'引擎连接状态：'"),
    ("'No graph data yet.'", "'暂无图谱数据。'"),
    ("No graph data yet. Building from observations and memories...",
     "暂无图谱数据。正在从观测和记忆构建..."),
    ("'Unknown session'", "'未知会话'"),
    ("'Untitled crystal'", "'未命名晶体'"),
    ("'Import failed'", "'导入失败'"),
    ("'Deleted via viewer'", "'通过查看器删除'"),
    ("'Dashboard failed to load: '", "'仪表盘加载失败：'"),
    ("'query failed / Retry'", "'查询失败 / 重试'"),
    ("'request failed'", "'请求失败'"),
    ("'no data yet'", "'暂无数据'"),
    ("'Open dashboard'", "'打开仪表盘'"),
    ("'Rebuild Graph'", "'重建图谱'"),
    ("'Showing '", "'显示 '"),
    ("'Shown: '", "'已显示: '"),
    ("'Imported '", "'已导入 '"),
    ("'Done'", "'完成'"),
    ("'Loading session details\u2026'", "'加载会话详情\u2026'"),
    ("'Importing JSONL\u2026'", "'导入 JSONL\u2026'"),
    ("'Loading replay\u2026'", "'加载回放\u2026'"),
    ("'Loading sessions\u2026'", "'加载会话\u2026'"),
    # 动态按钮文案
    ("btn.textContent = 'Summarize'", "btn.textContent = '生成摘要'"),
    ("btn.textContent = 'Summarizing", "btn.textContent = '摘要生成中"),
    # 主题切换
    ("'DARK'", "'深色'"), ("'LIGHT'", "'浅色'"),
    ("'End Session'", "'结束会话'"),
]

# 表格表头 / 控件（HTML 结构形态）
I18N_STRUCT = [
    ("<th>Project</th>", "<th>项目</th>"),
    ("<th>Function</th>", "<th>函数</th>"),
    ('<option value="">All types</option>', '<option value="">全部类型</option>'),
    (">Enter <code>", ">输入 <code>"),
    (">DARK<", ">深色<"),
    (">Speed<", ">速度<"),
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
