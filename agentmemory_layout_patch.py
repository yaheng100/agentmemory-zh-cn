#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agentmemory Viewer —— 会话页布局修复补丁
================================================================

问题（2026-09-11 实测截图确认）：
  会话(sessions)视图是两栏布局：
      grid-template-columns: minmax(300px, 400px) minmax(0, 1fr)
  但**未选中任何会话时**，右侧 #session-detail 是空的，却仍占着 1fr。
  结果：会话列表被压在最多 400px 的窄栏里，右面约 2/3 宽度全部空着；
  窄栏还把命令预览挤成 3~4 行折行，非常难看。

修复内容（v2，当前版本）：
  1) 未选中会话 → 列表铺满整行，固定 **三列** 卡片网格
     (repeat(3, minmax(0,1fr)))，卡片各自独立圆角；
     窄屏自动降级：<=1100px 两列，<=820px 单列。
  2) 选中会话 → 才切成 左列表(300~400px) + 右详情(1fr) 两栏。
  3) 命令预览裁到 2 行（-webkit-line-clamp），不再折行撑高卡片。
  4) 会话 ID 显示**完整 UUID**（原为 shortSessionId 的 head…tail 省略形态），
     并给 .session-meta 加 word-break: break-word 防止长 ID 撑破卡片。
  5) 清洗预览里的 Claude Code 包装标签：
     <command-message> / <command-name> / <command-args> / <local-command-*>
     让卡片直接显示可读的命令与参数。
     注意：firstPrompt 被存储层截断到约 200 字符，caveat 经常没有闭合
     标签，所以必须有"未闭合兜底"规则，否则整段英文提示会留在卡片上。

版本演化（脚本可处理任意一种起点）：
  v0 = 上游原始文件
  v1 = 第一次修复（自适应多列 auto-fill 380px + 省略 ID）
  v2 = 当前版本（固定三列 + 完整 ID + meta 可换行）
  每个替换点都带多个 old 变体，长的优先匹配，所以 v0 / v1 都能升到 v2。

用法：
  python agentmemory_layout_patch.py check    [--file <index.html>]
  python agentmemory_layout_patch.py apply    [--file <index.html>]
  python agentmemory_layout_patch.py restore  [--file <index.html>]

默认目标文件：
  E:/agentmemory/node_modules/@agentmemory/agentmemory/dist/viewer/index.html

说明：apply / restore 都会先在目标同目录留一份带时间戳的 .bak 备份。
"""

import argparse
import os
import shutil
import sys
import time

DEFAULT_FILE = (
    "E:/agentmemory/node_modules/@agentmemory/agentmemory/dist/viewer/index.html"
)

# ===========================================================================
# 替换点 1：两栏布局 → 未选中时固定三列卡片网格 / 选中才两栏
# ===========================================================================
OLD_CSS_LAYOUT_V0 = """    .sessions-layout {
      display: grid;
      grid-template-columns: minmax(300px, 400px) minmax(0, 1fr);
      gap: 20px;
      align-items: start;
    }
    .sessions-layout #session-detail { position: sticky; top: 0; min-width: 0; }
    .sessions-layout #session-detail .detail-panel { margin-top: 0; }
    @media (max-width: 1100px) {
      .sessions-layout { grid-template-columns: 1fr; }
      .sessions-layout #session-detail { position: static; }
    }
    .session-list { display: flex; flex-direction: column; gap: 0; }"""

OLD_CSS_LAYOUT_V1 = """    .sessions-layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 20px;
      align-items: start;
    }
    /* Only split into two panes once a session is actually selected.
       Previously the list stayed in a 400px column even with nothing
       selected, leaving two thirds of the width empty. */
    .sessions-layout.has-detail {
      grid-template-columns: minmax(300px, 400px) minmax(0, 1fr);
    }
    .sessions-layout #session-detail { position: sticky; top: 0; min-width: 0; }
    .sessions-layout #session-detail .detail-panel { margin-top: 0; }
    @media (max-width: 1100px) {
      .sessions-layout,
      .sessions-layout.has-detail { grid-template-columns: 1fr; }
      .sessions-layout #session-detail { position: static; }
    }
    /* Nothing selected yet: fill the row with an adaptive card grid
       instead of one narrow column. */
    .sessions-layout:not(.has-detail) .session-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 12px;
    }
    .sessions-layout:not(.has-detail) .session-item {
      border-bottom: 1px solid var(--border-light);
      border-radius: 6px;
    }
    .session-list { display: flex; flex-direction: column; gap: 0; }"""

NEW_CSS_LAYOUT = """    .sessions-layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 20px;
      align-items: start;
    }
    /* Only split into two panes once a session is actually selected.
       Previously the list stayed in a 400px column even with nothing
       selected, leaving two thirds of the width empty. */
    .sessions-layout.has-detail {
      grid-template-columns: minmax(300px, 400px) minmax(0, 1fr);
    }
    .sessions-layout #session-detail { position: sticky; top: 0; min-width: 0; }
    .sessions-layout #session-detail .detail-panel { margin-top: 0; }
    @media (max-width: 1100px) {
      .sessions-layout,
      .sessions-layout.has-detail { grid-template-columns: 1fr; }
      .sessions-layout #session-detail { position: static; }
      .sessions-layout:not(.has-detail) .session-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 820px) {
      .sessions-layout:not(.has-detail) .session-list { grid-template-columns: minmax(0, 1fr); }
    }
    /* Nothing selected yet: lay the list out as a fixed three-column card
       grid instead of one narrow column. */
    .sessions-layout:not(.has-detail) .session-list {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }
    .sessions-layout:not(.has-detail) .session-item {
      border-bottom: 1px solid var(--border-light);
      border-radius: 6px;
    }
    .session-list { display: flex; flex-direction: column; gap: 0; }"""

# ===========================================================================
# 替换点 2：预览裁 2 行 + meta 允许换行（完整 UUID 更长）
# ===========================================================================
OLD_CSS_META_V0 = """    .session-item .session-meta {
      font-size: 11px;
      color: var(--ink-muted);
      font-family: var(--font-mono);
    }"""

OLD_CSS_META_V1 = """    .session-item .session-meta {
      font-size: 11px;
      color: var(--ink-muted);
      font-family: var(--font-mono);
    }
    /* Clamp the prompt preview to two lines so long command lines no
       longer stretch a card to four lines of wrapping text. */
    .session-item .session-preview {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      word-break: break-word;
    }"""

NEW_CSS_META = """    .session-item .session-meta {
      font-size: 11px;
      color: var(--ink-muted);
      font-family: var(--font-mono);
      word-break: break-word;
    }
    /* Clamp the prompt preview to two lines so long command lines no
       longer stretch a card to four lines of wrapping text. */
    .session-item .session-preview {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      word-break: break-word;
    }"""

# ===========================================================================
# 替换点 3：渲染函数 —— 加清洗函数 + 按选中状态加 has-detail 类
# ===========================================================================
OLD_JS_RENDER = """    function renderSessions() {
      var el = document.getElementById('view-sessions');
      var items = state.sessions.items.slice().sort(function(a, b) {
        return (b.startedAt || '').localeCompare(a.startedAt || '');
      });

      var html = '<div class="sessions-layout"><div class="session-list">';"""

NEW_JS_RENDER = """    // Slash-command invocations reach the viewer as raw XML-ish wrapper
    // tags (<command-message>…</command-message> <command-name>… etc).
    // Strip the wrappers so the list shows a readable command + args.
    function cleanSessionPreview(text) {
      var s = String(text || '');
      // The stored first prompt is capped (~200 chars), so a caveat block
      // often arrives without its closing tag. Handle the paired form
      // first, then fall back to dropping everything after a bare open tag.
      s = s.replace(/<local-command-caveat>[\\s\\S]*?<\\/local-command-caveat>\\s*/gi, '');
      s = s.replace(/<local-command-caveat>[\\s\\S]*$/i, '');
      s = s.replace(/<local-command-stdout>[\\s\\S]*?<\\/local-command-stdout>\\s*/gi, '');
      s = s.replace(/<command-message>[\\s\\S]*?<\\/command-message>\\s*/gi, '');
      s = s.replace(/<\\/?(?:command-(?:name|args|message)|local-command-[a-z-]+)>/gi, ' ');
      return s.replace(/\\s+/g, ' ').trim();
    }

    function renderSessions() {
      var el = document.getElementById('view-sessions');
      var items = state.sessions.items.slice().sort(function(a, b) {
        return (b.startedAt || '').localeCompare(a.startedAt || '');
      });

      var html = '<div class="sessions-layout' + (state.sessions.selectedId ? ' has-detail' : '') + '"><div class="session-list">';"""

# ===========================================================================
# 替换点 4：预览改用清洗后的文本，长度放宽到 160
# ===========================================================================
OLD_JS_PREVIEW = """          var preview = s.firstPrompt || s.summary || '';
          if (preview) {
            html += '<div class="session-preview" style="font-size:13px;color:var(--ink);margin:4px 0;line-height:1.4;">' + esc(truncate(preview, 140)) + '</div>';
          }"""

NEW_JS_PREVIEW = """          var preview = cleanSessionPreview(s.firstPrompt || s.summary || '');
          if (preview) {
            html += '<div class="session-preview" style="font-size:13px;color:var(--ink);margin:4px 0;line-height:1.4;">' + esc(truncate(preview, 160)) + '</div>';
          }"""

# ===========================================================================
# 替换点 5：会话 ID 显示完整 UUID（不再 head…tail 省略）
# ===========================================================================
OLD_JS_SESSION_ID = """          html += '<div class="session-meta">' + esc(shortSessionId(s, 12) || 'missing id') + ' &middot; ' + esc(formatTime(s.startedAt));"""

NEW_JS_SESSION_ID = """          html += '<div class="session-meta">' + esc(sessionId(s) || 'missing id') + ' &middot; ' + esc(formatTime(s.startedAt));"""

PATCHES = [
    {
        "name": "CSS 两栏→固定三列网格",
        "olds": [OLD_CSS_LAYOUT_V0, OLD_CSS_LAYOUT_V1],
        "new": NEW_CSS_LAYOUT,
    },
    {
        "name": "CSS 预览裁 2 行 + meta 换行",
        "olds": [OLD_CSS_META_V0, OLD_CSS_META_V1],
        "new": NEW_CSS_META,
    },
    {
        "name": "JS 渲染 + 预览清洗函数",
        "olds": [OLD_JS_RENDER],
        "new": NEW_JS_RENDER,
    },
    {
        "name": "JS 预览调用清洗",
        "olds": [OLD_JS_PREVIEW],
        "new": NEW_JS_PREVIEW,
    },
    {
        "name": "JS 会话 ID 显示完整",
        "olds": [OLD_JS_SESSION_ID],
        "new": NEW_JS_SESSION_ID,
    },
]


def read(path):
    """读文件，返回 (归一化为 LF 的文本, 原始行尾)。

    viewer 的 index.html 是纯 CRLF（实测 4636 行全 CRLF）。补丁锚点用 LF
    书写，所以这里统一归一化成 LF 再匹配，写回时按原行尾还原。
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8")
    crlf = raw.count(b"\r\n")
    bare_lf = raw.count(b"\n") - crlf
    newline = "\r\n" if crlf >= bare_lf else "\n"
    return text.replace("\r\n", "\n"), newline


def write(path, text, newline):
    # 二进制写：不做隐式行尾转换，只按原样还原
    if newline != "\n":
        text = text.replace("\n", newline)
    with open(path, "wb") as fh:
        fh.write(text.encode("utf-8"))


def backup(path):
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dst = path + ".bak-layout-" + stamp
    shutil.copy2(path, dst)
    return dst


def find_old(text, patch):
    """按 ox 长度降序找第一个命中的 old（长的优先，避免短锚点吃长锚点）。"""
    for old in sorted(patch["olds"], key=len, reverse=True):
        if old in text:
            return old
    return None


def status_of(text, patch):
    if patch["new"] in text:
        return "applied"          # 已是修复后形态
    if find_old(text, patch) is not None:
        return "pending"          # 还是可识别的旧形态，可打补丁
    return "unknown"              # 都不匹配（被改过或版本不同）


def cmd_check(path):
    text, nl = read(path)
    print("[i] 目标文件: %s" % path)
    print("[i] 大小: %d 字节（行尾: %s）"
          % (os.path.getsize(path), "CRLF" if nl == "\r\n" else "LF"))
    print()
    pending = 0
    applied = 0
    for patch in PATCHES:
        st = status_of(text, patch)
        mark = {"applied": "[=] 已应用", "pending": "[ ] 待应用", "unknown": "[?] 未匹配"}[st]
        print("  %-26s %s" % (patch["name"], mark))
        if st == "pending":
            pending += 1
        elif st == "applied":
            applied += 1
    print()
    if pending == 0 and applied == len(PATCHES):
        print("[OK] 布局修复已全部应用。")
    elif pending and applied:
        print("[!] 部分应用：%d 项待应用。" % pending)
    elif pending:
        print("[i] 尚未应用，共 %d 项可打。" % pending)
    else:
        print("[!] 无法匹配任何锚点 —— 目标文件可能不是预期的 viewer 版本，请先确认。")
    return 0


def cmd_apply(path):
    text, nl = read(path)
    changed = []
    for patch in PATCHES:
        st = status_of(text, patch)
        if st == "applied":
            print("  =  %s（已应用，跳过）" % patch["name"])
            continue
        if st == "pending":
            old = find_old(text, patch)
            text = text.replace(old, patch["new"], 1)
            changed.append(patch["name"])
            print("  +  %s（已应用）" % patch["name"])
        else:
            print("  !  %s（锚点未匹配，跳过 —— 请人工确认）" % patch["name"])
    if not changed:
        print("\n[i] 没有需要改动的项。")
        return 0
    bak = backup(path)
    write(path, text, nl)
    print("\n[OK] 已应用 %d 项，写入 %s" % (len(changed), path))
    print("     备份: %s" % bak)
    print("     建议随后运行 tools/check_js_syntax.js 校验语法。")
    return 0


def cmd_restore(path):
    d = os.path.dirname(path)
    base = os.path.basename(path)
    cands = sorted(
        [f for f in os.listdir(d) if f.startswith(base + ".bak-layout-")],
        reverse=True,
    )
    if not cands:
        print("[!] 没找到本补丁的备份（%s.bak-layout-*）。" % base)
        return 1
    src = os.path.join(d, cands[0])
    shutil.copy2(src, path)
    print("[OK] 已从 %s 还原。" % src)
    return 0


def main():
    ap = argparse.ArgumentParser(description="agentmemory Viewer 会话页布局修复补丁")
    ap.add_argument("mode", choices=["check", "apply", "restore"])
    ap.add_argument("--file", default=DEFAULT_FILE, help="viewer index.html 路径")
    args = ap.parse_args()

    path = args.file
    if not os.path.isfile(path):
        print("[!] 找不到文件: %s" % path)
        return 1

    if args.mode == "check":
        return cmd_check(path)
    if args.mode == "apply":
        return cmd_apply(path)
    return cmd_restore(path)


if __name__ == "__main__":
    sys.exit(main())
