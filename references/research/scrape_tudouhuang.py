#!/usr/bin/env python3
"""抓取 scboy.cc 用户「土豆黄2024」(uid=89053) 动态时间线。

规则：
- 凭证只从同目录 .env 读取，不写死在代码里
- 每次抓 BATCH_SIZE 页，写一批 MD，然后休眠 SLEEP_SECONDS 秒
- 支持断点续跑（.scrape_progress.json）
"""

from __future__ import annotations

import hashlib
import html
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# --- 配置（不含密钥）---
BASE_URL = "https://www.scboy.cc/"
UID = 89053
USERNAME = "土豆黄2024"
TOTAL_PAGES = 267
BATCH_SIZE = int(os.environ.get("SCBOY_BATCH_SIZE", "10"))
SLEEP_SECONDS = int(os.environ.get("SCBOY_SLEEP_SECONDS", str(5 * 60)))
REQUEST_TIMEOUT = 30
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DIR = Path(__file__).resolve().parent
ENV_PATH = DIR / ".env"
PROGRESS_PATH = DIR / ".scrape_progress.json"
OUT_DIR = DIR / "tudouhuang-2024"


def load_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise SystemExit(
            f"缺少 {path}。请复制 .env.example 为 .env 并填写 "
            "SCBOY_MOBILE / SCBOY_PASSWORD（勿把 .env 提交到 git）。"
        )
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def html_to_text(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"</p\s*>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    text = html.unescape(fragment)
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in text.splitlines()]
    # 压缩多余空行，保留段落
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln.strip():
            blank += 1
            if blank <= 1 and out:
                out.append("")
            continue
        blank = 0
        out.append(ln.strip())
    return "\n".join(out).strip()


class ScboyClient:
    def __init__(self, mobile: str, password: str) -> None:
        self.mobile = mobile
        self.password = password
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [("User-Agent", USER_AGENT)]

    def login(self) -> None:
        pwd_md5 = hashlib.md5(self.password.encode("utf-8")).hexdigest()
        data = urllib.parse.urlencode(
            {"mobile": self.mobile, "password": pwd_md5}
        ).encode("utf-8")
        req = urllib.request.Request(
            BASE_URL + "?user-login.htm",
            data=data,
            method="POST",
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Referer": BASE_URL + "?user-login.htm",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        with self.opener.open(req, timeout=REQUEST_TIMEOUT) as resp:
            body = resp.read().decode("utf-8", "ignore")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"登录响应非 JSON: {body[:200]}") from exc
        if str(payload.get("code")) != "0":
            # 不回显服务端原文里可能夹带的敏感信息以外的字段
            raise RuntimeError(f"登录失败: code={payload.get('code')}")
        print("[login] ok", flush=True)

    def fetch(self, path_or_url: str) -> str:
        url = (
            path_or_url
            if path_or_url.startswith("http")
            else BASE_URL + path_or_url.lstrip("/")
        )
        req = urllib.request.Request(url)
        try:
            with self.opener.open(req, timeout=REQUEST_TIMEOUT) as resp:
                return resp.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                print("[session] expired, re-login", flush=True)
                self.login()
                with self.opener.open(req, timeout=REQUEST_TIMEOUT) as resp:
                    return resp.read().decode("utf-8", "ignore")
            raise


def timeline_url(page: int) -> str:
    return f"?user-{UID}-{page}.htm"


def abs_url(href: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    href = href if href.startswith("?") else "?" + href.lstrip("?/")
    return BASE_URL.rstrip("/") + "/" + href


ITEM_RE = re.compile(
    r'<li class="media post[^"]*">(.*?)</li>\s*(?=<li class="media post|</ul>|$)',
    re.S | re.I,
)


def parse_timeline_items(raw: str) -> list[dict]:
    items: list[dict] = []
    for block in ITEM_RE.findall(raw):
        time_m = re.search(
            r'class="ml-2 text-muted small"\s*>\s*([^<]+?)\s*<', block, re.S
        )
        time_str = time_m.group(1).strip() if time_m else ""

        if "发表了新主题" in block:
            kind = "thread"
            title_m = re.search(
                r'href="(\?thread-\d+\.htm)"[^>]*title="主题"\s*>\s*([^<]+?)\s*<',
                block,
                re.S,
            )
            if not title_m:
                title_m = re.search(
                    r'href="(\?thread-\d+\.htm)"[^>]*>\s*([^<]+?)\s*<',
                    block,
                    re.S,
                )
            thread_href = title_m.group(1) if title_m else ""
            title = html.unescape(title_m.group(2).strip()) if title_m else ""
            post_href = thread_href
            content = ""
        else:
            kind = "reply"
            action_m = re.search(
                r'对主题\s*<a[^>]*href="([^"]+)"[^>]*title="([^"]*)"[^>]*>\s*《([\s\S]*?)》\s*</a>\s*进行了回复',
                block,
                re.S,
            )
            if action_m:
                post_href = action_m.group(1)
                title = html.unescape(action_m.group(2).strip() or action_m.group(3).strip())
                # 主题链接去掉 #post
                thread_href = post_href.split("#", 1)[0]
            else:
                post_href = ""
                thread_href = ""
                title = ""
            body_m = re.search(
                r'<div class="mt-3">\s*<a class="text-dark"[^>]*>([\s\S]*?)</a>\s*</div>',
                block,
                re.S,
            )
            content = html_to_text(body_m.group(1)) if body_m else ""

        post_id = ""
        m_pid = re.search(r"#post_(\d+)", post_href)
        if m_pid:
            post_id = m_pid.group(1)
        tid_m = re.search(r"thread-(\d+)", thread_href or post_href)
        thread_id = tid_m.group(1) if tid_m else ""

        items.append(
            {
                "kind": kind,
                "time": time_str,
                "title": title,
                "content": content,
                "thread_id": thread_id,
                "post_id": post_id,
                "thread_url": abs_url(thread_href),
                "post_url": abs_url(post_href),
            }
        )
    return items


def extract_thread_op(raw: str) -> str:
    """取出主题一楼正文（isfirst=1）。"""
    m = re.search(
        r'<div class="message[^"]*"\s+isfirst="1">([\s\S]*?)'
        r'(?:<div class="share-component"|</div>\s*<div class="plugin")',
        raw,
        re.I,
    )
    if m:
        return html_to_text(m.group(1))
    m = re.search(
        r'<div class="message break-all"[^>]*>([\s\S]*?)</div>\s*<div class="plugin',
        raw,
        re.I,
    )
    if m:
        return html_to_text(m.group(1))
    return ""


def enrich_threads(client: ScboyClient, items: list[dict]) -> None:
    for it in items:
        if it["kind"] != "thread" or not it["thread_id"]:
            continue
        if it.get("content"):
            continue
        url = f"?thread-{it['thread_id']}.htm"
        try:
            raw = client.fetch(url)
            it["content"] = extract_thread_op(raw)
            time.sleep(1.0)  # 主题正文额外轻限速
        except Exception as exc:  # noqa: BLE001
            it["content"] = f"[抓取主题正文失败: {type(exc).__name__}]"
            print(f"[warn] thread {it['thread_id']}: {exc}", flush=True)


def md_escape_cell(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("|", "\\|").replace("\n", "<br>")
    return text


def render_batch_md(start: int, end: int, items: list[dict]) -> str:
    replies = [x for x in items if x["kind"] == "reply"]
    threads = [x for x in items if x["kind"] == "thread"]

    lines: list[str] = [
        f"# {USERNAME} 动态 · 第 {start}–{end} 页",
        "",
        f"- 来源：`{BASE_URL}?user-{UID}-N.htm`",
        f"- 页码范围：{start}–{end} / {TOTAL_PAGES}",
        f"- 本批条目：{len(items)}（回复 {len(replies)}，新主题 {len(threads)}）",
        "",
        "## 回复",
        "",
    ]
    if replies:
        lines += [
            "| 时间 | 回复的帖子 | 他说了什么 | 链接 |",
            "|------|------------|------------|------|",
        ]
        for it in replies:
            title = md_escape_cell(it["title"] or "(无标题)")
            body = md_escape_cell(it["content"] or "")
            link = it["post_url"] or it["thread_url"]
            lines.append(
                f"| {md_escape_cell(it['time'])} | {title} | {body} | {link} |"
            )
    else:
        lines.append("_本批无回复。_")

    lines += ["", "## 发表的主题", ""]
    if threads:
        for i, it in enumerate(threads, 1):
            lines.append(f"### {i}. {it['title'] or '(无标题)'}")
            lines.append("")
            lines.append(f"- 时间：{it['time']}")
            lines.append(f"- 链接：{it['thread_url']}")
            lines.append("- 正文：")
            lines.append("")
            body = it["content"] or "_（时间线仅有标题，正文未取到）_"
            lines.append(body)
            lines.append("")
    else:
        lines.append("_本批无新主题。_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def load_progress() -> dict:
    if PROGRESS_PATH.is_file():
        return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    return {"next_page": 1, "batches_done": []}


def save_progress(progress: dict) -> None:
    PROGRESS_PATH.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_batch(client: ScboyClient, start: int, end: int) -> list[dict]:
    all_items: list[dict] = []
    for page in range(start, end + 1):
        url = timeline_url(page)
        print(f"[fetch] page {page}: {url}", flush=True)
        raw = client.fetch(url)
        # 会员墙探测
        if "会员可读写" in raw and "sc-follow-timeline" not in raw:
            print("[session] wall detected, re-login", flush=True)
            client.login()
            raw = client.fetch(url)
        items = parse_timeline_items(raw)
        print(f"[parse] page {page}: {len(items)} items", flush=True)
        enrich_threads(client, items)
        for it in items:
            it["page"] = page
        all_items.extend(items)
        time.sleep(0.8)
    return all_items


def main() -> int:
    env = load_env(ENV_PATH)
    mobile = env.get("SCBOY_MOBILE", "").strip()
    password = env.get("SCBOY_PASSWORD", "").strip()
    if not mobile or not password:
        raise SystemExit(" .env 中 SCBOY_MOBILE / SCBOY_PASSWORD 不能为空")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = load_progress()
    next_page = int(progress.get("next_page", 1))
    if next_page > TOTAL_PAGES:
        print(f"[done] already finished (next_page={next_page})", flush=True)
        return 0

    client = ScboyClient(mobile, password)
    client.login()

    while next_page <= TOTAL_PAGES:
        end = min(next_page + BATCH_SIZE - 1, TOTAL_PAGES)
        start = next_page
        print(f"[batch] pages {start}-{end}", flush=True)
        items = run_batch(client, start, end)
        out_path = OUT_DIR / f"pages-{start:03d}-{end:03d}.md"
        out_path.write_text(render_batch_md(start, end, items), encoding="utf-8")
        print(f"[write] {out_path} ({len(items)} items)", flush=True)

        # 同步一份结构化备份，便于后续合并/校验（不含密钥）
        jsonl_path = OUT_DIR / f"pages-{start:03d}-{end:03d}.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as fh:
            for it in items:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")

        next_page = end + 1
        progress["next_page"] = next_page
        progress.setdefault("batches_done", []).append(
            {"start": start, "end": end, "items": len(items), "md": str(out_path.name)}
        )
        save_progress(progress)

        if next_page <= TOTAL_PAGES:
            print(
                f"[sleep] {SLEEP_SECONDS}s before next batch "
                f"(next page {next_page})",
                flush=True,
            )
            time.sleep(SLEEP_SECONDS)

    # 合并索引
    index_lines = [
        f"# {USERNAME} 动态抓取索引",
        "",
        f"- uid：{UID}",
        f"- 时间线页数：1–{TOTAL_PAGES}",
        f"- 输出目录：`{OUT_DIR.name}/`",
        "",
        "| 文件 | 页码 | 条目数 |",
        "|------|------|--------|",
    ]
    for b in progress.get("batches_done", []):
        index_lines.append(
            f"| `{b['md']}` | {b['start']}–{b['end']} | {b['items']} |"
        )
    (OUT_DIR / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print("[done] all pages scraped", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n[abort] interrupted; progress saved if last batch finished", flush=True)
        raise SystemExit(130)
