#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agentmemory Viewer 汉化复检工具：headless Chromium 逐 tab 真实渲染 + 提取可见文本 + 扫英文。

为什么需要它：`agentmemory_i18n_patch.py check` 只能命中**静态模板字符串**，
看不到运行时才拼出来的内容（数据表格、状态徽章、日期、空状态分支、JS 拼接句）。
本脚本把页面真正渲染出来再扫，是汉化完整性的最终闸门。

依赖：本机有 Chromium / Chrome / Edge 任一（默认找 Playwright 缓存，其次 Chrome / Edge）。
     纯标准库，无需安装任何包。

用法：
  python tools/render_scan_i18n.py                 # 渲染全部 12 个 tab 并扫描
  python tools/render_scan_i18n.py dashboard memories   # 只跑指定 tab
  python tools/render_scan_i18n.py --analyze-only  # 只分析上次渲染产物，不重新渲染
  python tools/render_scan_i18n.py --base http://localhost:3113 --out D:\\tmp\\vr

产物：--out 目录下每个 tab 一个 .html / .png / .err
结论：打印每个 tab 的「候选界面英文」行；理想结果 = 只剩品牌词（agentmemory / github）。
     timeline 里的代码 diff、audit 里的 JSON payload、actions 里的 curl 示例都是**数据**，
     刻意不翻译，属正常输出。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

DEFAULT_TABS = ["dashboard", "graph", "memories", "timeline", "sessions", "lessons",
                "actions", "crystals", "audit", "activity", "profile", "replay"]

DEFAULT_OUT = os.path.join(os.path.expanduser("~"), ".agentmemory-render-scan")

SKIP_TAGS = {"script", "style", "noscript", "svg", "path"}

# 品牌/技术词白名单：这些出现英文是正常的
WHITE = set("""agentmemory github claude code jsonl mcp api url uri id css html http https
OTel BM25 SSE REST JSON CLI SQL Viewer npm Node Windows macOS Linux csrf csp ui ux ai llm
ANTHROPIC_API_KEY GEMINI_API_KEY OPENAI_API_KEY VOYAGE_API_KEY COHERE_API_KEY OLLAMA_HOST
GRAPH_EXTRACTION_ENABLED CONSOLIDATION_ENABLED AGENTMEMORY_AUTO_COMPRESS AGENTMEMORY_SECRET
TODO FIXME NOTE WARN ERROR INFO DEBUG true false null undefined curl http localhost
title description priority rule reason confidence sessionId type content
""".split())

# 明显是"数据/命令/代码"的行特征 → 排除（这些是记忆内容，不该翻）
DATA_MARKERS = re.compile(
    r"(obs_|mem_|act_|cry_|ses_\w{6}|diff --git|^index |^--- |^\+\+\+ "
    r"|\.(java|ts|js|py|md|sql|json|ya?ml|cmd|bat|sh)\b"
    r"|[A-Za-z]:[\\\\/]|/e/Work|/c/Users|src[/\\\\]main"
    r"|\{\"|toolUseId|command\"|file_path|git -C|grep -n|sed -n|curl -X|npm |node "
    r"|post_tool_use|pre_tool_use|superpowers"
    r"|[0-9a-f]{12,}|^\s*\x22\w+\x22\s*:)"   # JSON 键值行（audit payload）
)


def find_chrome(explicit):
    """依次找 Playwright 缓存 Chromium → Chrome → Edge"""
    if explicit:
        return explicit
    cands = []
    pw = os.path.join(os.path.expanduser("~"), "AppData", "Local", "ms-playwright")
    if os.path.isdir(pw):
        for d in sorted(os.listdir(pw), reverse=True):
            if d.startswith("chromium-"):
                for sub in ("chrome-win64", "chrome-win"):
                    cands.append(os.path.join(pw, d, sub, "chrome.exe"))
    cands += [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        shutil.which("chrome") or "",
        shutil.which("chromium") or "",
    ]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    sys.exit("[!] 找不到 Chromium/Chrome/Edge，用 --chrome 指定可执行文件路径")


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip:
            self.parts.append(d)


def visible_lines(html):
    p = TextExtractor()
    p.feed(html)
    t = re.sub(r"[ \t\r\f\v]+", " ", "".join(p.parts))
    return [l.strip() for l in t.split("\n") if l.strip()]


def is_ui_english(line):
    """是否是『可能需要翻译的界面文案』（排除品牌词与数据行）"""
    if re.search(r"[\u4e00-\u9fff]", line):
        return False
    if len(line) > 90:                       # 长行几乎一定是数据/日志
        return False
    if DATA_MARKERS.search(line):
        return False
    words = re.findall(r"[A-Za-z]{2,}", line)
    if not words:
        return False
    if set(w.lower() for w in words) <= WHITE:
        return False                          # 纯品牌/技术词
    return bool(re.search(r"[A-Za-z]{3,}", line))


def render_all(chrome, base, tabs, out):
    os.makedirs(out, exist_ok=True)
    for tab in tabs:
        html_path = os.path.join(out, tab + ".html")
        png_path = os.path.join(out, tab + ".png")
        with open(html_path, "w", encoding="utf-8") as fo, \
                open(os.path.join(out, tab + ".err"), "w", encoding="utf-8") as fe:
            subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                            "--no-proxy-server", "--hide-scrollbars",
                            "--virtual-time-budget=15000", "--window-size=1600,1400",
                            "--dump-dom", base + "/#" + tab],
                           stdout=fo, stderr=fe, timeout=180)
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                        "--no-proxy-server", "--hide-scrollbars",
                        "--virtual-time-budget=15000", "--window-size=1600,1400",
                        "--screenshot=" + png_path, base + "/#" + tab],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
        print("[+] 渲染 %-10s -> %s (%dKB)" %
              (tab, png_path, os.path.getsize(png_path) // 1024 if os.path.exists(png_path) else 0))


def analyze(tabs, out):
    total = 0
    print("=" * 74)
    for tab in tabs:
        hp = os.path.join(out, tab + ".html")
        if not os.path.exists(hp):
            print("TAB %-10s （无渲染产物，跳过）" % tab)
            continue
        lines = visible_lines(open(hp, encoding="utf-8", errors="replace").read())
        bad = sorted({l for l in lines if is_ui_english(l)})
        total += len(bad)
        print("TAB %-10s 候选界面英文 %d 行" % (tab, len(bad)))
        for b in bad:
            print("     " + b[:110])
    print("=" * 74)
    print("合计候选界面英文行: %d" % total)
    print("判断标准：只剩 agentmemory / github 等品牌词 = 通过；")
    print("         timeline 的 diff、audit 的 JSON、actions 的 curl 示例是数据，不算漏翻。")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tabs", nargs="*", help="要检查的 tab，缺省全部 12 个")
    ap.add_argument("--base", default="http://localhost:3113")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--chrome", default=None)
    ap.add_argument("--analyze-only", action="store_true",
                    help="只分析上次渲染产物，不重新渲染")
    a = ap.parse_args()

    tabs = a.tabs or DEFAULT_TABS
    if not a.analyze_only:
        render_all(find_chrome(a.chrome), a.base.rstrip("/"), tabs, a.out)
    n = analyze(tabs, a.out)
    sys.exit(0 if n == 0 else 1)


if __name__ == "__main__":
    main()
